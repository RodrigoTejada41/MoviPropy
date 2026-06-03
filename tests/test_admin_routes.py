from fastapi.testclient import TestClient

from moviprogy_api.domain.auth import AdminSession
from moviprogy_api.domain.core import Cliente, Dispositivo, Midia, Playlist
from moviprogy_api.main import create_app
from moviprogy_api.security import hash_token


ADMIN_TOKEN = "test-admin-session"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


class FakeCoreRepository:
    def __init__(self) -> None:
        self.clientes: dict[str, Cliente] = {}
        self.dispositivos: dict[str, Dispositivo] = {}
        self.midias: dict[str, Midia] = {}
        self.playlists: dict[str, Playlist] = {}
        self.playlist_midias: list[tuple[str, str, int, int | None]] = []

    def save_cliente(self, cliente: Cliente) -> None:
        self.clientes[cliente.id] = cliente

    def get_cliente(self, cliente_id: str) -> Cliente | None:
        return self.clientes.get(cliente_id)

    def save_dispositivo(self, dispositivo: Dispositivo) -> None:
        self.dispositivos[dispositivo.id] = dispositivo

    def get_dispositivo(self, dispositivo_id: str) -> Dispositivo | None:
        return self.dispositivos.get(dispositivo_id)

    def save_midia(self, midia: Midia) -> None:
        self.midias[midia.id] = midia

    def get_midia(self, midia_id: str) -> Midia | None:
        return self.midias.get(midia_id)

    def save_playlist(self, playlist: Playlist) -> None:
        self.playlists[playlist.id] = playlist

    def get_playlist(self, playlist_id: str) -> Playlist | None:
        return self.playlists.get(playlist_id)

    def add_midia_to_playlist(
        self,
        playlist_id: str,
        midia_id: str,
        ordem: int,
        duracao_override: int | None = None,
    ) -> None:
        self.playlist_midias.append(
            (playlist_id, midia_id, ordem, duracao_override)
        )


class FakeAuthRepository:
    def __init__(self, perfil: str = "admin") -> None:
        self.sessions = {
            hash_token(ADMIN_TOKEN): AdminSession(
                user_id="user-001",
                perfil=perfil,
                ativo=True,
            )
        }

    def get_session(self, token_hash: str) -> AdminSession | None:
        return self.sessions.get(token_hash)


def _create_test_app(perfil: str = "admin"):
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    app.state.auth_repository = FakeAuthRepository(perfil=perfil)
    return app


def test_admin_rejects_missing_token():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/clientes",
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "token ausente"}


def test_admin_rejects_invalid_token():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/clientes",
        headers={"Authorization": "Bearer invalid"},
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "token invalido"}


def test_admin_rejects_non_admin_user():
    app = _create_test_app(perfil="operador")
    client = TestClient(app)

    response = client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "permissao insuficiente"}


def test_admin_creates_and_gets_cliente():
    app = _create_test_app()
    client = TestClient(app)

    create_response = client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um", "documento": "123"},
    )
    get_response = client.get(
        "/api/admin/clientes/cliente-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json() == {
        "id": "cliente-001",
        "nome": "Cliente Um",
        "documento": "123",
        "ativo": True,
    }
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == "Cliente Um"


def test_admin_returns_404_for_missing_cliente():
    app = _create_test_app()
    client = TestClient(app)

    response = client.get(
        "/api/admin/clientes/inexistente",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "cliente nao encontrado"}


def test_admin_creates_and_gets_dispositivo():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    create_response = client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )
    get_response = client.get(
        "/api/admin/dispositivos/device-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json()["codigo_ativacao"] == "CODE-001"
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == "TV Entrada"


def test_admin_rejects_dispositivo_for_missing_cliente():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-inexistente",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "cliente_id invalido"}


def test_admin_creates_and_gets_midia():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    create_response = client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
            "duracao_segundos": 30,
        },
    )
    get_response = client.get(
        "/api/admin/midias/midia-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json()["nome"] == "Video Entrada"
    assert get_response.status_code == 200
    assert get_response.json()["sha256"] == "a" * 64


def test_admin_rejects_midia_for_missing_cliente():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-inexistente",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "cliente_id invalido"}


def test_admin_creates_and_gets_playlist():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    create_response = client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={
            "id": "playlist-001",
            "cliente_id": "cliente-001",
            "nome": "Playlist Principal",
            "versao": 1,
            "ativa": True,
        },
    )
    get_response = client.get(
        "/api/admin/playlists/playlist-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json()["ativa"] is True
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == "Playlist Principal"


def test_admin_links_midia_to_playlist():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )
    client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={
            "id": "playlist-001",
            "cliente_id": "cliente-001",
            "nome": "Playlist Principal",
        },
    )

    response = client.post(
        "/api/admin/playlists/playlist-001/midias",
        headers=ADMIN_HEADERS,
        json={"midia_id": "midia-001", "ordem": 1, "duracao_override": 20},
    )

    assert response.status_code == 201
    assert response.json() == {
        "playlist_id": "playlist-001",
        "midia_id": "midia-001",
        "ordem": 1,
        "duracao_override": 20,
    }


def test_admin_rejects_link_when_midia_belongs_to_other_cliente():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-002", "nome": "Cliente Dois"},
    )
    client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )
    client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={
            "id": "playlist-001",
            "cliente_id": "cliente-002",
            "nome": "Playlist Cliente Dois",
        },
    )

    response = client.post(
        "/api/admin/playlists/playlist-001/midias",
        headers=ADMIN_HEADERS,
        json={"midia_id": "midia-001", "ordem": 1},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "midia de outro cliente"}
