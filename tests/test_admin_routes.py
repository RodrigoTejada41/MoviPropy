import hashlib
import errno
from pathlib import Path

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

    def list_clientes(
        self,
        limit: int = 50,
        offset: int = 0,
        ativo: bool | None = None,
    ) -> list[Cliente]:
        clientes = [
            cliente
            for cliente in self.clientes.values()
            if ativo is None or cliente.ativo is ativo
        ]
        return clientes[offset : offset + limit]

    def save_dispositivo(self, dispositivo: Dispositivo) -> None:
        self.dispositivos[dispositivo.id] = dispositivo

    def get_dispositivo(self, dispositivo_id: str) -> Dispositivo | None:
        return self.dispositivos.get(dispositivo_id)

    def list_dispositivos(
        self,
        limit: int = 50,
        offset: int = 0,
        cliente_id: str | None = None,
        bloqueado: bool | None = None,
    ) -> list[Dispositivo]:
        dispositivos = [
            dispositivo
            for dispositivo in self.dispositivos.values()
            if (cliente_id is None or dispositivo.cliente_id == cliente_id)
            and (bloqueado is None or dispositivo.bloqueado is bloqueado)
        ]
        return dispositivos[offset : offset + limit]

    def save_midia(self, midia: Midia) -> None:
        self.midias[midia.id] = midia

    def get_midia(self, midia_id: str) -> Midia | None:
        return self.midias.get(midia_id)

    def list_midias(
        self,
        limit: int = 50,
        offset: int = 0,
        cliente_id: str | None = None,
        ativo: bool | None = None,
    ) -> list[Midia]:
        midias = [
            midia
            for midia in self.midias.values()
            if (cliente_id is None or midia.cliente_id == cliente_id)
            and (ativo is None or midia.ativo is ativo)
        ]
        return midias[offset : offset + limit]

    def save_playlist(self, playlist: Playlist) -> None:
        self.playlists[playlist.id] = playlist

    def get_playlist(self, playlist_id: str) -> Playlist | None:
        return self.playlists.get(playlist_id)

    def list_playlists(
        self,
        limit: int = 50,
        offset: int = 0,
        cliente_id: str | None = None,
        ativa: bool | None = None,
    ) -> list[Playlist]:
        playlists = [
            playlist
            for playlist in self.playlists.values()
            if (cliente_id is None or playlist.cliente_id == cliente_id)
            and (ativa is None or playlist.ativa is ativa)
        ]
        return playlists[offset : offset + limit]

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

    def get_player_events_for_device(self, device_id: str) -> dict[str, list[dict]]:
        if device_id not in self.dispositivos:
            return {"status": [], "logs": [], "sync": []}
        return {
            "status": [{"status": "online", "versao_player": "0.1.0"}],
            "logs": [{"nivel": "info", "evento": "teste", "dados": {}}],
            "sync": [{"playlist_id": "playlist-001", "versao": 1, "status": "ok"}],
        }


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


def test_admin_lists_clientes():
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

    response = client.get("/api/admin/clientes", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    assert [cliente["id"] for cliente in response.json()] == [
        "cliente-001",
        "cliente-002",
    ]


def test_admin_lists_clientes_with_pagination_and_active_filter():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id, ativo in (
        ("cliente-001", True),
        ("cliente-002", False),
        ("cliente-003", True),
    ):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id, "ativo": ativo},
        )

    response = client.get(
        "/api/admin/clientes?ativo=true&limit=1&offset=1",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert [cliente["id"] for cliente in response.json()] == ["cliente-003"]


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


def test_admin_lists_dispositivos():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )

    response = client.get("/api/admin/dispositivos", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    assert response.json()[0]["id"] == "device-001"


def test_admin_lists_dispositivos_with_cliente_and_blocked_filters():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id in ("cliente-001", "cliente-002"):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id},
        )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV 1",
            "codigo_ativacao": "CODE-001",
            "bloqueado": False,
        },
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-002",
            "cliente_id": "cliente-001",
            "nome": "TV 2",
            "codigo_ativacao": "CODE-002",
            "bloqueado": True,
        },
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-003",
            "cliente_id": "cliente-002",
            "nome": "TV 3",
            "codigo_ativacao": "CODE-003",
            "bloqueado": True,
        },
    )

    response = client.get(
        "/api/admin/dispositivos?cliente_id=cliente-001&bloqueado=true",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert [dispositivo["id"] for dispositivo in response.json()] == ["device-002"]


def test_admin_gets_dispositivo_events():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )

    response = client.get(
        "/api/admin/dispositivos/device-001/eventos",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"][0]["status"] == "online"


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


def test_admin_lists_midias():
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

    response = client.get("/api/admin/midias", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    assert response.json()[0]["id"] == "midia-001"


def test_admin_lists_midias_with_cliente_and_active_filters():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id in ("cliente-001", "cliente-002"):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id},
        )
    for midia_id, cliente_id, ativo in (
        ("midia-001", "cliente-001", True),
        ("midia-002", "cliente-001", False),
        ("midia-003", "cliente-002", False),
    ):
        client.post(
            "/api/admin/midias",
            headers=ADMIN_HEADERS,
            json={
                "id": midia_id,
                "cliente_id": cliente_id,
                "nome": midia_id,
                "tipo": "video",
                "caminho": f"media/{midia_id}.mp4",
                "tamanho": 1024,
                "sha256": "a" * 64,
                "ativo": ativo,
            },
        )

    response = client.get(
        "/api/admin/midias?cliente_id=cliente-001&ativo=false",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert [midia["id"] for midia in response.json()] == ["midia-002"]


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


def test_admin_uploads_valid_video_midia(tmp_path):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    content = b"video-content"

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={
            "cliente_id": "cliente-001",
            "tipo": "video",
            "duracao_segundos": "30",
        },
        files={"arquivo": ("entrada.mp4", content, "video/mp4")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["cliente_id"] == "cliente-001"
    assert payload["nome"] == "entrada.mp4"
    assert payload["tipo"] == "video"
    assert payload["tamanho"] == len(content)
    assert payload["sha256"] == hashlib.sha256(content).hexdigest()
    saved = app.state.media_dir / payload["caminho"]
    assert saved.read_bytes() == content
    assert app.state.core_repository.get_midia(payload["id"]) == Midia(**payload)


def test_admin_upload_rejects_invalid_file_type(tmp_path):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={"cliente_id": "cliente-001", "tipo": "video"},
        files={"arquivo": ("entrada.exe", b"invalid", "application/octet-stream")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "arquivo invalido"}
    assert app.state.core_repository.midias == {}


def test_admin_upload_rejects_file_over_size_limit(tmp_path):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    app.state.max_upload_bytes = 4
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={"cliente_id": "cliente-001", "tipo": "video"},
        files={"arquivo": ("entrada.mp4", b"12345", "video/mp4")},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "arquivo excede tamanho maximo"}
    assert app.state.core_repository.midias == {}
    assert not any((tmp_path / "media").rglob("*"))


def test_admin_upload_handles_cross_device_tmp_and_media_dirs(
    tmp_path,
    monkeypatch,
):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    app.state.tmp_dir = tmp_path / "tmp"
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    def fail_replace(self, target):
        raise OSError(errno.EXDEV, "Invalid cross-device link")

    monkeypatch.setattr(Path, "replace", fail_replace)

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={"cliente_id": "cliente-001", "tipo": "video"},
        files={"arquivo": ("entrada.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 201
    saved = app.state.media_dir / response.json()["caminho"]
    assert saved.read_bytes() == b"video"


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


def test_admin_lists_playlists():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
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

    response = client.get("/api/admin/playlists", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    assert response.json()[0]["id"] == "playlist-001"


def test_admin_lists_playlists_with_cliente_and_active_filters():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id in ("cliente-001", "cliente-002"):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id},
        )
    for playlist_id, cliente_id, ativa in (
        ("playlist-001", "cliente-001", True),
        ("playlist-002", "cliente-001", False),
        ("playlist-003", "cliente-002", False),
    ):
        client.post(
            "/api/admin/playlists",
            headers=ADMIN_HEADERS,
            json={
                "id": playlist_id,
                "cliente_id": cliente_id,
                "nome": playlist_id,
                "ativa": ativa,
            },
        )

    response = client.get(
        "/api/admin/playlists?cliente_id=cliente-001&ativa=false",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert [playlist["id"] for playlist in response.json()] == ["playlist-002"]


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
