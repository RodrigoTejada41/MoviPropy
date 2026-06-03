from fastapi.testclient import TestClient

from moviprogy_api.domain.core import Dispositivo
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


def test_player_activation_returns_device_token():
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


def test_player_playlist_returns_active_manifest_for_valid_token():
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
