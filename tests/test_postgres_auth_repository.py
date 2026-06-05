import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import psycopg

from moviprogy_api.domain.auth import AdminAccessAudit, AdminSession, UserAccount
from moviprogy_api.repositories.postgres_auth import PostgresAuthRepository
from moviprogy_api.repositories.postgres_devices import run_migrations
from moviprogy_api.security import hash_password, hash_token, verify_password


DATABASE_URL = os.getenv("DATABASE_URL")


pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL nao configurado",
)


def test_postgres_auth_repository_persists_user_and_session():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresAuthRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    user = UserAccount(
        id=f"user-{suffix}",
        nome="Admin Teste",
        email=f"admin-{suffix}@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin",
        ativo=True,
    )
    token = f"token-{suffix}"

    repository.save_user(user)
    repository.save_session(
        hash_token(token),
        AdminSession(
            user_id=user.id,
            perfil=user.perfil,
            ativo=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ),
    )

    persisted_user = repository.get_user_by_email(user.email.upper())
    persisted_session = repository.get_session(hash_token(token))

    assert persisted_user is not None
    assert persisted_user.id == user.id
    assert persisted_user.senha_hash != "senha-segura"
    assert verify_password("senha-segura", persisted_user.senha_hash)
    assert persisted_session is not None
    assert persisted_session.user_id == user.id
    assert persisted_session.perfil == "admin"

    repository.delete_session(hash_token(token))

    assert repository.get_session(hash_token(token)) is None


def test_postgres_auth_repository_checks_cliente_permissions():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresAuthRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    user = UserAccount(
        id=f"user-rbac-{suffix}",
        nome="Admin Cliente",
        email=f"rbac-{suffix}@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin_cliente",
        ativo=True,
    )
    cliente_id = f"cliente-rbac-{suffix}"

    repository.save_user(user)
    repository.link_user_cliente(user.id, cliente_id)
    repository.grant_permission(user.id, "midias", "criar", cliente_id)

    assert repository.has_cliente_access(user.id, cliente_id) is True
    assert repository.has_permission(user.id, "midias", "criar", cliente_id) is True
    assert repository.has_permission(user.id, "midias", "excluir", cliente_id) is False
    assert repository.has_cliente_access(user.id, f"outro-{cliente_id}") is False


def test_postgres_auth_repository_lists_users_links_and_permissions():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresAuthRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    user = UserAccount(
        id=f"user-management-{suffix}",
        nome=f"Operador {suffix}",
        email=f"management-{suffix}@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="operador",
        ativo=True,
    )
    cliente_id = f"cliente-management-{suffix}"

    repository.save_user(user)
    repository.link_user_cliente(user.id, cliente_id)
    permission_id = repository.grant_permission(
        user.id,
        "midias",
        "upload",
        cliente_id,
    )

    assert repository.get_user_by_id(user.id) == user
    assert repository.list_users(perfil="operador", limit=10_000).count(user) == 1
    assert repository.count_users(perfil="operador") >= 1
    assert repository.list_user_clientes(user.id)[0].cliente_id == cliente_id
    permissions = repository.list_user_permissions(user.id)
    assert permissions[0].id == permission_id
    assert permissions[0].recurso == "midias"
    assert permissions[0].acao == "upload"
    assert permissions[0].cliente_id == cliente_id


def test_postgres_auth_repository_persists_admin_access_audit():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresAuthRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    user = UserAccount(
        id=f"user-audit-{suffix}",
        nome="Admin Auditoria",
        email=f"audit-{suffix}@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin",
        ativo=True,
    )
    audit = AdminAccessAudit(
        user_id=user.id,
        cliente_id=f"cliente-audit-{suffix}",
        recurso="midias",
        acao="criar",
        status="permitido",
        ip="127.0.0.1",
        user_agent="pytest",
    )

    repository.save_user(user)
    repository.record_admin_access(
        user_id=audit.user_id,
        recurso=audit.recurso,
        acao=audit.acao,
        status=audit.status,
        cliente_id=audit.cliente_id,
        ip=audit.ip,
        user_agent=audit.user_agent,
    )

    audits = repository.list_admin_access_audits(
        user_id=user.id,
        cliente_id=audit.cliente_id,
        recurso=audit.recurso,
        acao=audit.acao,
        status=audit.status,
        limit=1,
        offset=0,
    )

    assert audits[0].user_id == audit.user_id
    assert audits[0].cliente_id == audit.cliente_id
    assert audits[0].recurso == audit.recurso
    assert audits[0].acao == audit.acao
    assert audits[0].status == audit.status
    assert audits[0].ip == audit.ip
    assert audits[0].user_agent == audit.user_agent
    assert (
        repository.count_admin_access_audits(
            user_id=user.id,
            cliente_id=audit.cliente_id,
            recurso=audit.recurso,
            acao=audit.acao,
            status=audit.status,
        )
        == 1
    )

    old_audit_id = f"audit-old-{suffix}"
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            """
            INSERT INTO auditoria_acessos (
                id,
                user_id,
                cliente_id,
                recurso,
                acao,
                status,
                criado_em
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                old_audit_id,
                user.id,
                audit.cliente_id,
                "clientes",
                "ler",
                "permitido",
                datetime.now(timezone.utc) - timedelta(days=200),
            ),
        )
        connection.commit()

    deleted = repository.delete_admin_access_audits_older_than(
        datetime.now(timezone.utc) - timedelta(days=180)
    )

    assert deleted >= 1
    with psycopg.connect(DATABASE_URL) as connection:
        old_row = connection.execute(
            "SELECT 1 FROM auditoria_acessos WHERE id = %s",
            (old_audit_id,),
        ).fetchone()
    assert old_row is None
