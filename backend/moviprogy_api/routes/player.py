from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import FileResponse

from moviprogy_api.domain.devices import ActivationRequest, ActivationResult
from moviprogy_api.domain.player_events import (
    PlayerLogEvent,
    PlayerLogPayload,
    PlayerStatusEvent,
    PlayerStatusPayload,
    SyncConfirmation,
    SyncConfirmationPayload,
)
from moviprogy_api.domain.sync import PlaylistManifest


router = APIRouter(prefix="/api/player", tags=["player"])


@router.post("/ativar", response_model=ActivationResult)
def activate_player(
    payload: ActivationRequest,
    request: Request,
) -> ActivationResult:
    repository = getattr(request.app.state, "core_repository", None)
    if repository is not None:
        dispositivo = repository.get_dispositivo_by_activation_code(
            payload.activation_code
        )
        if dispositivo is not None:
            manifest = repository.get_playlist_manifest_for_device(dispositivo.id)
            playlist_version = manifest.version if manifest is not None else 1
            return request.app.state.device_registry.activate_device(
                device_id=dispositivo.id,
                request=payload,
                playlist_version=playlist_version,
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="codigo de ativacao invalido",
        )

    result = request.app.state.device_registry.activate(payload)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="codigo de ativacao invalido",
        )
    return result


@router.get("/playlist", response_model=PlaylistManifest)
def get_active_playlist(
    request: Request,
    authorization: str | None = Header(default=None),
) -> PlaylistManifest:
    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo ausente",
        )

    manifest = None
    repository = getattr(request.app.state, "core_repository", None)
    session = request.app.state.device_registry.get_session(token)
    if session is not None and repository is not None:
        manifest = repository.get_playlist_manifest_for_device(session.device_id)

    if manifest is None:
        manifest = request.app.state.device_registry.get_manifest(token)

    if manifest is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo invalido",
        )
    return manifest


@router.get("/atualizacao")
def check_player_update(
    playlist_versao_atual: int,
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, int | bool]:
    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo ausente",
        )
    session = request.app.state.device_registry.get_session(token)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo invalido",
        )
    manifest = _device_manifest(request, session.device_id, token)
    if manifest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="playlist ativa nao encontrada",
        )
    return {
        "possui_atualizacao": manifest.version > playlist_versao_atual,
        "nova_versao": manifest.version,
    }


@router.get("/midias/{midia_id}/download")
def download_media(
    midia_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
) -> FileResponse:
    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo ausente",
        )

    session = request.app.state.device_registry.get_session(token)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo invalido",
        )

    repository = getattr(request.app.state, "core_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="repository indisponivel",
        )

    midia = repository.get_downloadable_midia_for_device(
        session.device_id,
        midia_id,
    )
    if midia is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="midia fora da playlist atual",
        )

    media_dir = Path(request.app.state.media_dir)
    file_path = _safe_media_path(media_dir, midia.caminho)
    if file_path is None or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="arquivo da midia nao encontrado",
        )

    return FileResponse(
        file_path,
        media_type=_media_type(midia.tipo),
        filename=Path(midia.caminho).name,
    )


@router.post("/status", status_code=status.HTTP_202_ACCEPTED)
def record_player_status(
    payload: PlayerStatusPayload,
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    session = _device_session(request, authorization)
    repository = _core_repository(request)
    repository.save_player_status(
        PlayerStatusEvent(device_id=session.device_id, **payload.model_dump())
    )
    return {"status": "registrado"}


@router.post("/logs", status_code=status.HTTP_202_ACCEPTED)
def record_player_log(
    payload: PlayerLogPayload,
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    session = _device_session(request, authorization)
    repository = _core_repository(request)
    repository.save_player_log(
        PlayerLogEvent(device_id=session.device_id, **payload.model_dump())
    )
    return {"status": "registrado"}


@router.post("/sincronizacao/confirmar", status_code=status.HTTP_202_ACCEPTED)
def confirm_player_sync(
    payload: SyncConfirmationPayload,
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    session = _device_session(request, authorization)
    repository = _core_repository(request)
    repository.save_sync_confirmation(
        SyncConfirmation(device_id=session.device_id, **payload.model_dump())
    )
    return {"status": "registrado"}


def _device_session(request: Request, authorization: str | None):
    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo ausente",
        )
    session = request.app.state.device_registry.get_session(token)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token do dispositivo invalido",
        )
    return session


def _device_manifest(
    request: Request,
    device_id: str,
    token: str,
) -> PlaylistManifest | None:
    repository = getattr(request.app.state, "core_repository", None)
    if repository is not None:
        return repository.get_playlist_manifest_for_device(device_id)
    return request.app.state.device_registry.get_manifest(token)


def _core_repository(request: Request):
    repository = getattr(request.app.state, "core_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="repository indisponivel",
        )
    return repository


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def _safe_media_path(media_dir: Path, stored_path: str) -> Path | None:
    base_path = media_dir.resolve()
    candidate = (base_path / stored_path).resolve()
    try:
        candidate.relative_to(base_path)
    except ValueError:
        return None
    return candidate


def _media_type(tipo: str) -> str:
    if tipo == "video":
        return "video/mp4"
    if tipo == "imagem":
        return "image/jpeg"
    return "application/octet-stream"
