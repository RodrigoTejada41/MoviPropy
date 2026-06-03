import json
import hashlib
from pathlib import Path
from secrets import token_urlsafe

from pydantic import BaseModel, Field

from moviprogy_api.domain.sync import PlaylistManifest


class ActivationRequest(BaseModel):
    activation_code: str = Field(min_length=1)
    hardware_id: str = Field(min_length=1)
    player_version: str = Field(min_length=1)


class ActivationResult(BaseModel):
    device_id: str
    token: str
    playlist_version: int


class DeviceSession(BaseModel):
    device_id: str
    hardware_id: str
    player_version: str


class DeviceSessionRepository:
    def save_session(self, token_hash: str, session: DeviceSession) -> None:
        raise NotImplementedError

    def get_session(self, token_hash: str) -> DeviceSession | None:
        raise NotImplementedError


class DeviceRegistry:
    def __init__(
        self,
        data_file: Path | None = None,
        repository: DeviceSessionRepository | None = None,
    ) -> None:
        self._activation_codes = {
            "MOVI-DEMO-001": "device-demo-001",
        }
        self._data_file = data_file
        self._repository = repository
        self._sessions: dict[str, DeviceSession] = (
            {} if repository is not None else self._load_sessions()
        )
        self._manifests = {
            "device-demo-001": PlaylistManifest(
                playlist_id="playlist-demo-001",
                version=1,
                files=[],
            )
        }

    def activate(self, request: ActivationRequest) -> ActivationResult | None:
        device_id = self._activation_codes.get(request.activation_code)
        if device_id is None:
            return None

        manifest = self._manifests[device_id]
        return self.activate_device(
            device_id=device_id,
            request=request,
            playlist_version=manifest.version,
        )

    def activate_device(
        self,
        device_id: str,
        request: ActivationRequest,
        playlist_version: int,
    ) -> ActivationResult:
        token = token_urlsafe(32)
        token_hash = _token_hash(token)
        session = DeviceSession(
            device_id=device_id,
            hardware_id=request.hardware_id,
            player_version=request.player_version,
        )
        if self._repository is not None:
            self._repository.save_session(token_hash, session)
        else:
            self._sessions[token_hash] = session
            self._save_sessions()
        return ActivationResult(
            device_id=device_id,
            token=token,
            playlist_version=playlist_version,
        )

    def get_session(self, token: str) -> DeviceSession | None:
        token_hash = _token_hash(token)
        if self._repository is not None:
            return self._repository.get_session(token_hash)
        return self._sessions.get(token_hash)

    def get_manifest(self, token: str) -> PlaylistManifest | None:
        session = self.get_session(token)

        if session is None:
            return None
        return self._manifests.get(session.device_id)

    def _load_sessions(self) -> dict[str, DeviceSession]:
        if self._data_file is None:
            return {}

        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._data_file.exists():
            self._write_json({"sessions": {}})
            return {}

        with self._data_file.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        return {
            token: DeviceSession(**session)
            for token, session in payload.get("sessions", {}).items()
        }

    def _save_sessions(self) -> None:
        if self._data_file is None:
            return

        payload = {
            "sessions": {
                token: session.model_dump()
                for token, session in self._sessions.items()
            }
        }
        self._write_json(payload)

    def _write_json(self, payload: dict[str, object]) -> None:
        if self._data_file is None:
            return

        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self._data_file.with_suffix(".tmp")
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, sort_keys=True)
        temp_file.replace(self._data_file)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
