from datetime import datetime, timezone

from fastapi.testclient import TestClient

from moviprogy_api.domain.core import Cliente
from moviprogy_api.domain.google_drive import GoogleDriveFolder, GoogleDriveStatus
from moviprogy_api.main import create_app
from test_admin_routes import ADMIN_HEADERS, FakeAuthRepository, FakeCoreRepository


class FakeGoogleDriveRepository:
    def __init__(self) -> None:
        self.states: dict[str, tuple[str, datetime, bool]] = {}
        self.status = GoogleDriveStatus(connected=False, status="desconectado")
        self.folders: list[GoogleDriveFolder] = []
        self.files = []
        self.operations = []
        self.access_token_encrypted = ""
        self.refresh_token_encrypted = ""
        self.metadata: dict[str, dict] = {}

    def save_oauth_state(self, state: str, user_id: str, expires_at: datetime) -> None:
        self.states[state] = (user_id, expires_at, False)

    def consume_oauth_state(self, state: str) -> str | None:
        record = self.states.get(state)
        if record is None:
            return None
        user_id, expires_at, used = record
        if used or expires_at <= datetime.now(timezone.utc):
            return None
        self.states[state] = (user_id, expires_at, True)
        return user_id

    def save_integration(
        self,
        connected_email,
        access_token_encrypted,
        refresh_token_encrypted,
        expires_at,
        status="connected",
    ):
        self.access_token_encrypted = access_token_encrypted
        self.refresh_token_encrypted = refresh_token_encrypted
        self.status = GoogleDriveStatus(
            connected=True,
            status=status,
            email=connected_email,
            connected_at=datetime.now(timezone.utc),
        )
        return "google-drive"

    def disconnect(self):
        self.status = GoogleDriveStatus(connected=False, status="desconectado")

    def get_status(self):
        return self.status

    def save_root_folder(self, folder_id: str, folder_name: str):
        if not self.status.connected:
            raise RuntimeError("google drive desconectado")
        folder = GoogleDriveFolder(id=folder_id, name=folder_name, status="ok")
        self.folders = [folder, *[item for item in self.folders if item.cliente_id]]
        self.status.root_folder_id = folder_id
        self.status.root_folder_name = folder_name
        return folder

    def save_client_folder(self, cliente_id: str, folder_id: str, folder_name: str):
        folder = GoogleDriveFolder(
            id=folder_id,
            name=folder_name,
            status="ok",
            cliente_id=cliente_id,
        )
        self.folders.append(folder)
        return folder

    def list_folders(self):
        return self.folders

    def list_files(self, cliente_id=None, folder_id=None):
        return [
            item
            for item in self.files
            if (cliente_id is None or item.cliente_id == cliente_id)
            and (folder_id is None or item.id == folder_id)
        ]

    def save_imported_media_metadata(
        self,
        midia_id,
        file_id,
        folder_id,
        mime_type,
        web_view_link,
    ):
        self.metadata[midia_id] = {
            "file_id": file_id,
            "folder_id": folder_id,
            "mime_type": mime_type,
            "web_view_link": web_view_link,
        }

    def validate_access(self):
        self.status.last_validation_at = datetime.now(timezone.utc)
        return self.status

    def record_operation(self, **kwargs):
        self.operations.append(kwargs)


def _create_test_app():
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    app.state.auth_repository = FakeAuthRepository()
    app.state.google_drive_repository = FakeGoogleDriveRepository()
    return app


def test_google_drive_status_requires_admin_session():
    app = _create_test_app()
    client = TestClient(app)

    response = client.get("/api/integrations/google-drive/status")

    assert response.status_code == 401


def test_google_drive_connect_returns_authorization_url(monkeypatch):
    app = _create_test_app()
    client = TestClient(app)
    monkeypatch.setenv("MOVIPROGY_GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("MOVIPROGY_GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv(
        "MOVIPROGY_GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8000/api/integrations/google-drive/callback",
    )

    response = client.post("/api/integrations/google-drive/connect", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["authorization_url"].startswith("https://accounts.google.com")
    assert payload["state"] in app.state.google_drive_repository.states


def test_google_drive_connect_simulated_without_google_credentials(monkeypatch):
    app = _create_test_app()
    client = TestClient(app)
    monkeypatch.setenv("MOVIPROGY_GOOGLE_OAUTH_SIMULATED", "true")
    monkeypatch.setenv(
        "MOVIPROGY_GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8000/api/integrations/google-drive/callback",
    )

    response = client.post("/api/integrations/google-drive/connect", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["authorization_url"].startswith(
        "http://127.0.0.1:8000/api/integrations/google-drive/callback?code=simulated-code"
    )
    assert payload["state"] in app.state.google_drive_repository.states


def test_google_drive_callback_encrypts_tokens(monkeypatch):
    app = _create_test_app()
    client = TestClient(app)
    monkeypatch.setenv("MOVIPROGY_GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("MOVIPROGY_GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv(
        "MOVIPROGY_GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8000/api/integrations/google-drive/callback",
    )
    monkeypatch.setenv("MOVIPROGY_GOOGLE_TOKEN_KEY", "x" * 32)
    monkeypatch.setenv("MOVIPROGY_GOOGLE_OAUTH_SIMULATED", "true")

    connect_response = client.post(
        "/api/integrations/google-drive/connect",
        headers=ADMIN_HEADERS,
    )
    state = connect_response.json()["state"]
    response = client.get(
        f"/api/integrations/google-drive/callback?code=code-001&state={state}"
    )

    assert response.status_code == 200
    assert app.state.google_drive_repository.status.connected is True
    assert "simulated-access-token" not in app.state.google_drive_repository.access_token_encrypted
    assert "simulated-refresh-token" not in app.state.google_drive_repository.refresh_token_encrypted


def test_google_drive_root_and_client_folder_flow(monkeypatch):
    app = _create_test_app()
    app.state.google_drive_repository.status = GoogleDriveStatus(
        connected=True,
        status="connected",
        email="drive@moviprogy.local",
    )
    app.state.core_repository.save_cliente(Cliente(id="cliente-001", nome="Cliente Um"))
    client = TestClient(app)

    root_response = client.post(
        "/api/integrations/google-drive/root-folder",
        headers=ADMIN_HEADERS,
        json={"folder_name": "MoviProgy_Midias", "create_if_missing": True},
    )
    client_response = client.post(
        "/api/integrations/google-drive/client-folder",
        headers=ADMIN_HEADERS,
        json={"cliente_id": "cliente-001", "folder_name": "Cliente_001"},
    )

    assert root_response.status_code == 200
    assert root_response.json()["name"] == "MoviProgy_Midias"
    assert client_response.status_code == 200
    assert client_response.json()["cliente_id"] == "cliente-001"


def test_google_drive_import_media_creates_midia_metadata():
    app = _create_test_app()
    app.state.google_drive_repository.status = GoogleDriveStatus(
        connected=True,
        status="connected",
        email="drive@moviprogy.local",
    )
    app.state.core_repository.save_cliente(Cliente(id="cliente-001", nome="Cliente Um"))
    client = TestClient(app)

    response = client.post(
        "/api/integrations/google-drive/import-media",
        headers=ADMIN_HEADERS,
        json={
            "cliente_id": "cliente-001",
            "file_id": "drive-file-001",
            "tipo": "video",
            "nome": "video.mp4",
            "tamanho": 12,
            "sha256": "a" * 64,
            "folder_id": "folder-001",
            "google_drive_mime_type": "video/mp4",
            "google_drive_web_view_link": "https://drive.google.com/file/d/drive-file-001",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["caminho"] == "google_drive/drive-file-001"
    assert app.state.google_drive_repository.metadata[payload["id"]]["file_id"] == "drive-file-001"
