from fastapi import APIRouter, Header, HTTPException, Request, status

from moviprogy_api.domain.devices import ActivationRequest, ActivationResult
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


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token
