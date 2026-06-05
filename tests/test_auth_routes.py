from fastapi.testclient import TestClient

from moviprogy_api.domain.auth import AdminSession, UserAccount
from moviprogy_api.main import create_app
from moviprogy_api.security import hash_password, hash_token


class FakeAuthRepository:
    def __init__(self) -> None:
        self.users: dict[str, UserAccount] = {}
        self.sessions: dict[str, AdminSession] = {}

    def get_user_by_email(self, email: str) -> UserAccount | None:
        return self.users.get(email.lower())

    def save_session(self, token_hash: str, session: AdminSession) -> None:
        self.sessions[token_hash] = session

    def get_session(self, token_hash: str) -> AdminSession | None:
        return self.sessions.get(token_hash)

    def delete_session(self, token_hash: str) -> None:
        self.sessions.pop(token_hash, None)

    def get_user_by_id(self, user_id: str) -> UserAccount | None:
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None


def test_login_returns_admin_access_token():
    app = create_app()
    auth_repository = FakeAuthRepository()
    auth_repository.users["admin@moviprogy.local"] = UserAccount(
        id="user-001",
        nome="Admin",
        email="admin@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin",
        ativo=True,
    )
    app.state.auth_repository = auth_repository
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@moviprogy.local", "senha": "senha-segura"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["usuario"] == {
        "id": "user-001",
        "nome": "Admin",
        "email": "admin@moviprogy.local",
        "perfil": "admin",
    }
    assert hash_token(body["access_token"]) in auth_repository.sessions


def test_login_rejects_invalid_password():
    app = create_app()
    auth_repository = FakeAuthRepository()
    auth_repository.users["admin@moviprogy.local"] = UserAccount(
        id="user-001",
        nome="Admin",
        email="admin@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin",
        ativo=True,
    )
    app.state.auth_repository = auth_repository
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@moviprogy.local", "senha": "errada"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "credenciais invalidas"}


def test_login_rejects_inactive_user():
    app = create_app()
    auth_repository = FakeAuthRepository()
    auth_repository.users["admin@moviprogy.local"] = UserAccount(
        id="user-001",
        nome="Admin",
        email="admin@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin",
        ativo=False,
    )
    app.state.auth_repository = auth_repository
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@moviprogy.local", "senha": "senha-segura"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "credenciais invalidas"}


def test_refresh_replaces_admin_access_token():
    app = create_app()
    auth_repository = FakeAuthRepository()
    auth_repository.users["admin@moviprogy.local"] = UserAccount(
        id="user-001",
        nome="Admin",
        email="admin@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin",
        ativo=True,
    )
    app.state.auth_repository = auth_repository
    client = TestClient(app)
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@moviprogy.local", "senha": "senha-segura"},
    )
    old_token = login_response.json()["access_token"]

    response = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {old_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["access_token"] != old_token
    assert hash_token(old_token) not in auth_repository.sessions
    assert hash_token(body["access_token"]) in auth_repository.sessions


def test_logout_invalidates_admin_access_token():
    app = create_app()
    auth_repository = FakeAuthRepository()
    auth_repository.users["admin@moviprogy.local"] = UserAccount(
        id="user-001",
        nome="Admin",
        email="admin@moviprogy.local",
        senha_hash=hash_password("senha-segura"),
        perfil="admin",
        ativo=True,
    )
    app.state.auth_repository = auth_repository
    client = TestClient(app)
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@moviprogy.local", "senha": "senha-segura"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "logout efetuado"}
    assert hash_token(token) not in auth_repository.sessions
    blocked_response = client.get(
        "/api/admin/clientes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert blocked_response.status_code == 403
