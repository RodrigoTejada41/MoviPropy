import hashlib
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)

from moviprogy_api.domain.core import (
    Cliente,
    Dispositivo,
    Midia,
    Playlist,
    PlaylistMidia,
    PlaylistMidiaRequest,
)
from moviprogy_api.security import require_admin_permission, require_admin_user


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_user)],
)

_ALLOWED_UPLOADS = {
    "video": {
        ".mp4": "video/mp4",
    },
    "imagem": {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    },
}


@router.post(
    "/clientes",
    response_model=Cliente,
    status_code=status.HTTP_201_CREATED,
)
def create_cliente(cliente: Cliente, request: Request) -> Cliente:
    repository = _core_repository(request)
    require_admin_permission(request, "clientes", "criar")
    repository.save_cliente(cliente)
    return cliente


@router.get("/clientes", response_model=list[Cliente])
def list_clientes(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ativo: bool | None = None,
) -> list[Cliente]:
    repository = _core_repository(request)
    require_admin_permission(request, "clientes", "ler")
    return repository.list_clientes(limit=limit, offset=offset, ativo=ativo)


@router.get("/clientes/{cliente_id}", response_model=Cliente)
def get_cliente(cliente_id: str, request: Request) -> Cliente:
    repository = _core_repository(request)
    require_admin_permission(request, "clientes", "ler", cliente_id)
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
    require_admin_permission(
        request,
        "dispositivos",
        "criar",
        dispositivo.cliente_id,
    )
    repository.save_dispositivo(dispositivo)
    return dispositivo


@router.get("/dispositivos", response_model=list[Dispositivo])
def list_dispositivos(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    cliente_id: str | None = None,
    bloqueado: bool | None = None,
) -> list[Dispositivo]:
    repository = _core_repository(request)
    _require_scoped_list_permission(request, "dispositivos", "ler", cliente_id)
    return repository.list_dispositivos(
        limit=limit,
        offset=offset,
        cliente_id=cliente_id,
        bloqueado=bloqueado,
    )


@router.get("/dispositivos/{dispositivo_id}/eventos")
def get_dispositivo_events(dispositivo_id: str, request: Request) -> dict[str, list[dict]]:
    repository = _core_repository(request)
    dispositivo = repository.get_dispositivo(dispositivo_id)
    if dispositivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="dispositivo nao encontrado",
        )
    require_admin_permission(request, "logs", "ler", dispositivo.cliente_id)
    return repository.get_player_events_for_device(dispositivo_id)


@router.get("/dispositivos/{dispositivo_id}", response_model=Dispositivo)
def get_dispositivo(dispositivo_id: str, request: Request) -> Dispositivo:
    repository = _core_repository(request)
    dispositivo = repository.get_dispositivo(dispositivo_id)
    if dispositivo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="dispositivo nao encontrado",
        )
    require_admin_permission(request, "dispositivos", "ler", dispositivo.cliente_id)
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
    require_admin_permission(request, "midias", "criar", midia.cliente_id)
    repository.save_midia(midia)
    return midia


@router.get("/midias", response_model=list[Midia])
def list_midias(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    cliente_id: str | None = None,
    ativo: bool | None = None,
) -> list[Midia]:
    repository = _core_repository(request)
    _require_scoped_list_permission(request, "midias", "ler", cliente_id)
    return repository.list_midias(
        limit=limit,
        offset=offset,
        cliente_id=cliente_id,
        ativo=ativo,
    )


@router.post(
    "/midias/upload",
    response_model=Midia,
    status_code=status.HTTP_201_CREATED,
)
async def upload_midia(
    request: Request,
    cliente_id: str = Form(min_length=1),
    tipo: str = Form(min_length=1),
    duracao_segundos: int | None = Form(default=None, ge=0),
    arquivo: UploadFile = File(),
) -> Midia:
    repository = _core_repository(request)
    if repository.get_cliente(cliente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cliente_id invalido",
        )
    require_admin_permission(request, "midias", "upload", cliente_id)

    suffix = Path(arquivo.filename or "").suffix.lower()
    if not _is_allowed_upload(tipo, suffix, arquivo.content_type):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="arquivo invalido",
        )

    media_id = f"midia-{uuid4().hex}"
    relative_path = Path("clientes") / cliente_id / "midias" / media_id / f"original{suffix}"
    temp_dir = Path(request.app.state.tmp_dir) / "uploads"
    final_path = Path(request.app.state.media_dir) / relative_path
    temp_path = temp_dir / f"{media_id}{suffix}"
    max_upload_bytes = request.app.state.max_upload_bytes
    temp_dir.mkdir(parents=True, exist_ok=True)

    digest = hashlib.sha256()
    size = 0
    with temp_path.open("wb") as handle:
        while chunk := await arquivo.read(1024 * 1024):
            size += len(chunk)
            if size > max_upload_bytes:
                handle.close()
                temp_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="arquivo excede tamanho maximo",
                )
            digest.update(chunk)
            handle.write(chunk)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(temp_path), final_path)

    midia = Midia(
        id=media_id,
        cliente_id=cliente_id,
        nome=arquivo.filename or final_path.name,
        tipo=tipo,
        caminho=relative_path.as_posix(),
        tamanho=size,
        sha256=digest.hexdigest(),
        duracao_segundos=duracao_segundos,
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
    require_admin_permission(request, "midias", "ler", midia.cliente_id)
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
    require_admin_permission(request, "playlists", "criar", playlist.cliente_id)
    repository.save_playlist(playlist)
    return playlist


@router.get("/playlists", response_model=list[Playlist])
def list_playlists(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    cliente_id: str | None = None,
    ativa: bool | None = None,
) -> list[Playlist]:
    repository = _core_repository(request)
    _require_scoped_list_permission(request, "playlists", "ler", cliente_id)
    return repository.list_playlists(
        limit=limit,
        offset=offset,
        cliente_id=cliente_id,
        ativa=ativa,
    )


@router.get("/playlists/{playlist_id}", response_model=Playlist)
def get_playlist(playlist_id: str, request: Request) -> Playlist:
    repository = _core_repository(request)
    playlist = repository.get_playlist(playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="playlist nao encontrada",
        )
    require_admin_permission(request, "playlists", "ler", playlist.cliente_id)
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
    require_admin_permission(request, "playlists", "editar", playlist.cliente_id)
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


def _is_allowed_upload(
    tipo: str,
    suffix: str,
    content_type: str | None,
) -> bool:
    allowed = _ALLOWED_UPLOADS.get(tipo)
    if allowed is None:
        return False
    expected_content_type = allowed.get(suffix)
    return expected_content_type is not None and content_type == expected_content_type


def _core_repository(request: Request):
    repository = getattr(request.app.state, "core_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="repository indisponivel",
        )
    return repository


def _require_scoped_list_permission(
    request: Request,
    recurso: str,
    acao: str,
    cliente_id: str | None,
) -> None:
    session = getattr(request.state, "admin_session", None)
    if session is not None and session.perfil not in {"admin", "super_admin"}:
        if cliente_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="cliente_id obrigatorio",
            )
    require_admin_permission(request, recurso, acao, cliente_id)
