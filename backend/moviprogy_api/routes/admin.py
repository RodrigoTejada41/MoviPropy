from fastapi import APIRouter, Depends, HTTPException, Request, status

from moviprogy_api.domain.core import (
    Cliente,
    Dispositivo,
    Midia,
    Playlist,
    PlaylistMidia,
    PlaylistMidiaRequest,
)
from moviprogy_api.security import require_admin_user


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_user)],
)


@router.post(
    "/clientes",
    response_model=Cliente,
    status_code=status.HTTP_201_CREATED,
)
def create_cliente(cliente: Cliente, request: Request) -> Cliente:
    repository = _core_repository(request)
    repository.save_cliente(cliente)
    return cliente


@router.get("/clientes/{cliente_id}", response_model=Cliente)
def get_cliente(cliente_id: str, request: Request) -> Cliente:
    repository = _core_repository(request)
    cliente = repository.get_cliente(cliente_id)
    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="cliente nao encontrado",
        )
    return cliente


@router.post(
    "/dispositivos",
    response_model=Dispositivo,
    status_code=status.HTTP_201_CREATED,
)
def create_dispositivo(dispositivo: Dispositivo, request: Request) -> Dispositivo:
    repository = _core_repository(request)
    if repository.get_cliente(dispositivo.cliente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cliente_id invalido",
        )
    repository.save_dispositivo(dispositivo)
    return dispositivo


@router.get("/dispositivos/{dispositivo_id}", response_model=Dispositivo)
def get_dispositivo(dispositivo_id: str, request: Request) -> Dispositivo:
    repository = _core_repository(request)
    dispositivo = repository.get_dispositivo(dispositivo_id)
    if dispositivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="dispositivo nao encontrado",
        )
    return dispositivo


@router.post(
    "/midias",
    response_model=Midia,
    status_code=status.HTTP_201_CREATED,
)
def create_midia(midia: Midia, request: Request) -> Midia:
    repository = _core_repository(request)
    if repository.get_cliente(midia.cliente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cliente_id invalido",
        )
    repository.save_midia(midia)
    return midia


@router.get("/midias/{midia_id}", response_model=Midia)
def get_midia(midia_id: str, request: Request) -> Midia:
    repository = _core_repository(request)
    midia = repository.get_midia(midia_id)
    if midia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="midia nao encontrada",
        )
    return midia


@router.post(
    "/playlists",
    response_model=Playlist,
    status_code=status.HTTP_201_CREATED,
)
def create_playlist(playlist: Playlist, request: Request) -> Playlist:
    repository = _core_repository(request)
    if repository.get_cliente(playlist.cliente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cliente_id invalido",
        )
    repository.save_playlist(playlist)
    return playlist


@router.get("/playlists/{playlist_id}", response_model=Playlist)
def get_playlist(playlist_id: str, request: Request) -> Playlist:
    repository = _core_repository(request)
    playlist = repository.get_playlist(playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="playlist nao encontrada",
        )
    return playlist


@router.post(
    "/playlists/{playlist_id}/midias",
    response_model=PlaylistMidia,
    status_code=status.HTTP_201_CREATED,
)
def add_midia_to_playlist(
    playlist_id: str,
    payload: PlaylistMidiaRequest,
    request: Request,
) -> PlaylistMidia:
    repository = _core_repository(request)
    playlist = repository.get_playlist(playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="playlist nao encontrada",
        )
    midia = repository.get_midia(payload.midia_id)
    if midia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="midia nao encontrada",
        )
    if midia.cliente_id != playlist.cliente_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="midia de outro cliente",
        )
    repository.add_midia_to_playlist(
        playlist_id,
        payload.midia_id,
        payload.ordem,
        payload.duracao_override,
    )
    return PlaylistMidia(
        playlist_id=playlist_id,
        midia_id=payload.midia_id,
        ordem=payload.ordem,
        duracao_override=payload.duracao_override,
    )


def _core_repository(request: Request):
    repository = getattr(request.app.state, "core_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="repository indisponivel",
        )
    return repository
