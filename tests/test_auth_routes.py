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
