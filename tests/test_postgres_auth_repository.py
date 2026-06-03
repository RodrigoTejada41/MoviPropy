import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from moviprogy_api.domain.auth import AdminSession, UserAccount
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
