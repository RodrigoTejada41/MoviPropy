from fastapi.testclient import TestClient

from moviprogy_api.domain.core import Dispositivo, Midia
from moviprogy_api.domain.sync import MediaFile, PlaylistManifest
from moviprogy_api.main import create_app


class FakeCoreRepository:
    def __init__(self) -> None:
        self.dispositivo = Dispositivo(
            id="device-real-001",
            cliente_id="cliente-001",
            nome="TV Real",
            codigo_ativacao="REAL-CODE-001",
            playlist_atual_id="playlist-real-001",
        )
        self.manifest = PlaylistManifest(
            playlist_id="playlist-real-001",
            version=3,
            files=[
                MediaFile(
                    file_name="media/video-real.mp4",
                    size=2048,
                    sha256="b" * 64,
                )
            ],
        )
        self.midias = {
            "midia-real-001": Midia(
                id="midia-real-001",
                cliente_id="cliente-001",
                nome="Video Real",
                tipo="video",
                caminho="media/video-real.mp4",
                tamanho=2048,
                sha256="b" * 64,
            )
        }
        self.status_events = []
        self.log_events = []
        self.sync_confirmations = []

    def get_dispositivo_by_activation_code(
        self,
        activation_code: str,
    ) -> Dispositivo | None:
        if activation_code == self.dispositivo.codigo_ativacao:
            return self.dispositivo
        return None

    def get_playlist_manifest_for_device(
        self,
        device_id: str,
    ) -> PlaylistManifest | None:
        if device_id == self.dispositivo.id:
            return self.manifest
        return None

    def get_downloadable_midia_for_device(
        self,
        device_id: str,
        midia_id: str,
    ) -> Midia | None:
        if device_id != self.dispositivo.id:
            return None
        return self.midias.get(midia_id)

    def save_player_status(self, event) -> None:
        self.status_events.append(event)

    def save_player_log(self, event) -> None:
        self.log_events.append(event)

    def save_sync_confirmation(self, confirmation) -> None:
        self.sync_confirmations.append(confirmation)


def test_player_activation_returns_device_token(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    client = TestClient(create_app())

    response = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "MOVI-DEMO-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["device_id"] == "device-demo-001"
    assert body["token"]
    assert body["playlist_version"] == 1


def test_player_activation_uses_real_device_activation_code():
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    client = TestClient(app)

    response = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["device_id"] == "device-real-001"
    assert body["token"]
    assert body["playlist_version"] == 3


def test_player_activation_with_repository_rejects_demo_fallback_code():
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    client = TestClient(app)

    response = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "MOVI-DEMO-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "codigo de ativacao invalido"}


def test_player_activation_rejects_invalid_code():
    client = TestClient(create_app())

    response = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "INVALID",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "codigo de ativacao invalido"}


def test_player_playlist_requires_bearer_token():
    client = TestClient(create_app())

    response = client.get("/api/player/playlist")

    assert response.status_code == 401
    assert response.json() == {"detail": "token do dispositivo ausente"}


def test_player_playlist_returns_active_manifest_for_valid_token(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    client = TestClient(create_app())
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "MOVI-DEMO-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.get(
        "/api/player/playlist",
        headers={"Authorization": f"Bearer {activation['token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "playlist_id": "playlist-demo-001",
        "version": 1,
        "files": [],
    }


def test_player_playlist_returns_real_manifest_for_activated_device():
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.get(
        "/api/player/playlist",
        headers={"Authorization": f"Bearer {activation['token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "playlist_id": "playlist-real-001",
        "version": 3,
        "files": [
            {
                "file_name": "media/video-real.mp4",
                "size": 2048,
                "sha256": "b" * 64,
            }
        ],
    }


def test_player_media_download_requires_bearer_token():
    client = TestClient(create_app())

    response = client.get("/api/player/midias/midia-real-001/download")

    assert response.status_code == 401
    assert response.json() == {"detail": "token do dispositivo ausente"}


def test_player_media_download_rejects_media_outside_device_playlist(tmp_path):
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    app.state.media_dir = tmp_path
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.get(
        "/api/player/midias/midia-invalida/download",
        headers={"Authorization": f"Bearer {activation['token']}"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "midia fora da playlist atual"}


def test_player_media_download_returns_404_when_file_is_missing(tmp_path):
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    app.state.media_dir = tmp_path
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.get(
        "/api/player/midias/midia-real-001/download",
        headers={"Authorization": f"Bearer {activation['token']}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "arquivo da midia nao encontrado"}


def test_player_media_download_returns_file_for_current_playlist(tmp_path):
    media_file = tmp_path / "media" / "video-real.mp4"
    media_file.parent.mkdir(parents=True)
    media_file.write_bytes(b"video-content")
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    app.state.media_dir = tmp_path
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.get(
        "/api/player/midias/midia-real-001/download",
        headers={"Authorization": f"Bearer {activation['token']}"},
    )

    assert response.status_code == 200
    assert response.content == b"video-content"
    assert response.headers["content-length"] == str(len(b"video-content"))


def test_player_status_requires_bearer_token():
    client = TestClient(create_app())

    response = client.post(
        "/api/player/status",
        json={"status": "online", "versao_player": "0.1.0"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "token do dispositivo ausente"}


def test_player_status_records_device_status():
    app = create_app()
    repository = FakeCoreRepository()
    app.state.core_repository = repository
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.post(
        "/api/player/status",
        headers={"Authorization": f"Bearer {activation['token']}"},
        json={
            "status": "online",
            "playlist_atual": "playlist-real-001",
            "versao_player": "0.1.0",
            "espaco_livre": 1024,
        },
    )

    assert response.status_code == 202
    assert response.json() == {"status": "registrado"}
    assert repository.status_events[0].device_id == "device-real-001"
    assert repository.status_events[0].status == "online"


def test_player_logs_records_device_log():
    app = create_app()
    repository = FakeCoreRepository()
    app.state.core_repository = repository
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.post(
        "/api/player/logs",
        headers={"Authorization": f"Bearer {activation['token']}"},
        json={
            "nivel": "info",
            "evento": "download_concluido",
            "dados": {"midia_id": "midia-real-001"},
        },
    )

    assert response.status_code == 202
    assert response.json() == {"status": "registrado"}
    assert repository.log_events[0].device_id == "device-real-001"
    assert repository.log_events[0].evento == "download_concluido"


def test_player_sync_confirmation_records_success():
    app = create_app()
    repository = FakeCoreRepository()
    app.state.core_repository = repository
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.post(
        "/api/player/sincronizacao/confirmar",
        headers={"Authorization": f"Bearer {activation['token']}"},
        json={
            "playlist_id": "playlist-real-001",
            "versao": 3,
            "arquivos_baixados": ["midia-real-001"],
            "status": "concluida",
        },
    )

    assert response.status_code == 202
    assert response.json() == {"status": "registrado"}
    assert repository.sync_confirmations[0].device_id == "device-real-001"
    assert repository.sync_confirmations[0].status == "concluida"


def test_player_update_check_requires_bearer_token():
    client = TestClient(create_app())

    response = client.get(
        "/api/player/atualizacao",
        params={"playlist_versao_atual": 1},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "token do dispositivo ausente"}


def test_player_update_check_returns_false_when_playlist_is_current():
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.get(
        "/api/player/atualizacao",
        headers={"Authorization": f"Bearer {activation['token']}"},
        params={"playlist_versao_atual": 3},
    )

    assert response.status_code == 200
    assert response.json() == {
        "possui_atualizacao": False,
        "nova_versao": 3,
    }


def test_player_update_check_returns_true_when_remote_playlist_is_newer():
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    client = TestClient(app)
    activation = client.post(
        "/api/player/ativar",
        json={
            "activation_code": "REAL-CODE-001",
            "hardware_id": "BOX-001",
            "player_version": "0.1.0",
        },
    ).json()

    response = client.get(
        "/api/player/atualizacao",
        headers={"Authorization": f"Bearer {activation['token']}"},
        params={"playlist_versao_atual": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "possui_atualizacao": True,
        "nova_versao": 3,
    }
