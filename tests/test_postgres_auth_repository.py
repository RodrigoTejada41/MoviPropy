import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest

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
