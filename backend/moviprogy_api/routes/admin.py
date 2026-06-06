import hashlib
import shutil
from datetime import datetime, timedelta, timezone
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
    ClienteListResponse,
    ClienteUpdateRequest,
    Dispositivo,
    DispositivoListResponse,
    DispositivoUpdateRequest,
    Midia,
    MidiaListResponse,
    MidiaUpdateRequest,
    OperationalConfiguration,
    Playlist,
    PlaylistListResponse,
    PlaylistMidia,
    PlaylistMidiaRequest,
    PlaylistUpdateRequest,
)
from moviprogy_api.domain.auth import (
    AdminAccessAuditListResponse,
    AdminUserCreateRequest,
    AdminUserListResponse,
    AdminUserPublic,
    AdminUserUpdateRequest,
    AuditRetentionResponse,
    PermissionGrantRequest,
    PermissionPublic,
    UserAccount,
    UserClienteLink,
    UserClienteLinkRequest,
)
from moviprogy_api.security import (
    hash_password,
    record_admin_access,
    require_admin_permission,
    require_admin_user,
)
from moviprogy_api.domain.player_events import AdminSyncConfirmationListResponse


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


@router.get("/configuracoes", response_model=OperationalConfiguration)
def get_operational_configuration(request: Request) -> OperationalConfiguration:
    require_admin_permission(request, "configuracoes", "ler")
    return OperationalConfiguration(
        storage_provider="local",
        max_upload_bytes=request.app.state.max_upload_bytes,
        offline_first=True,
    )


@router.post(
    "/usuarios",
    response_model=AdminUserPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: AdminUserCreateRequest,
    request: Request,
) -> AdminUserPublic:
    repository = _auth_repository(request)
    require_admin_permission(request, "usuarios", "criar")
    existing = repository.get_user_by_email(payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        )
    user = UserAccount(
        id=payload.id or f"user-{uuid4().hex}",
        nome=payload.nome,
        email=payload.email.lower(),
        senha_hash=hash_password(payload.senha),
        perfil=payload.perfil,
        ativo=payload.ativo,
    )
    repository.save_user(user)
    return _user_public(user)


@router.get("/usuarios", response_model=AdminUserListResponse)
def list_users(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ativo: bool | None = None,
    perfil: str | None = None,
) -> AdminUserListResponse:
    repository = _auth_repository(request)
    require_admin_permission(request, "usuarios", "ler")
    return AdminUserListResponse(
        items=[
            _user_public(user)
            for user in repository.list_users(
                limit=limit,
                offset=offset,
                ativo=ativo,
                perfil=perfil,
            )
        ],
        limit=limit,
        offset=offset,
        total=repository.count_users(ativo=ativo, perfil=perfil),
    )


@router.get("/usuarios/{user_id}", response_model=AdminUserPublic)
def get_user(user_id: str, request: Request) -> AdminUserPublic:
    repository = _auth_repository(request)
    require_admin_permission(request, "usuarios", "ler")
    user = _get_user_or_404(repository, user_id)
    return _user_public(user)


@router.patch("/usuarios/{user_id}", response_model=AdminUserPublic)
def update_user(
    user_id: str,
    payload: AdminUserUpdateRequest,
    request: Request,
) -> AdminUserPublic:
    repository = _auth_repository(request)
    require_admin_permission(request, "usuarios", "editar")
    current = _get_user_or_404(repository, user_id)
    email = payload.email.lower() if payload.email is not None else current.email
    existing = repository.get_user_by_email(email)
    if existing is not None and existing.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        )
    updated = UserAccount(
        id=current.id,
        nome=payload.nome if payload.nome is not None else current.nome,
        email=email,
        senha_hash=(
            hash_password(payload.senha)
            if payload.senha is not None
            else current.senha_hash
        ),
        perfil=payload.perfil if payload.perfil is not None else current.perfil,
        ativo=payload.ativo if payload.ativo is not None else current.ativo,
    )
    repository.save_user(updated)
    return _user_public(updated)


@router.post(
    "/usuarios/{user_id}/clientes",
    response_model=UserClienteLink,
    status_code=status.HTTP_201_CREATED,
)
def link_user_cliente(
    user_id: str,
    payload: UserClienteLinkRequest,
    request: Request,
) -> UserClienteLink:
    auth_repository = _auth_repository(request)
    core_repository = _core_repository(request)
    _get_user_or_404(auth_repository, user_id)
    if core_repository.get_cliente(payload.cliente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cliente_id invalido",
        )
    require_admin_permission(
        request,
        "usuarios",
        "administrar",
        payload.cliente_id,
    )
    auth_repository.link_user_cliente(user_id, payload.cliente_id, payload.ativo)
    return UserClienteLink(
        user_id=user_id,
        cliente_id=payload.cliente_id,
        ativo=payload.ativo,
    )


@router.get("/usuarios/{user_id}/clientes", response_model=list[UserClienteLink])
def list_user_clientes(user_id: str, request: Request) -> list[UserClienteLink]:
    repository = _auth_repository(request)
    require_admin_permission(request, "usuarios", "ler")
    _get_user_or_404(repository, user_id)
    return repository.list_user_clientes(user_id)


@router.post(
    "/usuarios/{user_id}/permissoes",
    response_model=PermissionPublic,
    status_code=status.HTTP_201_CREATED,
)
def grant_user_permission(
    user_id: str,
    payload: PermissionGrantRequest,
    request: Request,
) -> PermissionPublic:
    auth_repository = _auth_repository(request)
    _get_user_or_404(auth_repository, user_id)
    if payload.cliente_id is not None:
        core_repository = _core_repository(request)
        if core_repository.get_cliente(payload.cliente_id) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cliente_id invalido",
            )
    require_admin_permission(
        request,
        "usuarios",
        "administrar",
        payload.cliente_id,
    )
    permission_id = auth_repository.grant_permission(
        user_id=user_id,
        recurso=payload.recurso,
        acao=payload.acao,
        cliente_id=payload.cliente_id,
        permitido=payload.permitido,
    )
    return PermissionPublic(
        id=permission_id,
        user_id=user_id,
        recurso=payload.recurso,
        acao=payload.acao,
        cliente_id=payload.cliente_id,
        permitido=payload.permitido,
    )


@router.get("/usuarios/{user_id}/permissoes", response_model=list[PermissionPublic])
def list_user_permissions(user_id: str, request: Request) -> list[PermissionPublic]:
    repository = _auth_repository(request)
    require_admin_permission(request, "usuarios", "ler")
    _get_user_or_404(repository, user_id)
    return repository.list_user_permissions(user_id)


@router.get("/auditoria/acessos", response_model=AdminAccessAuditListResponse)
def list_admin_access_audits(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: str | None = None,
    cliente_id: str | None = None,
    recurso: str | None = None,
    acao: str | None = None,
    status: str | None = None,
) -> AdminAccessAuditListResponse:
    repository = _auth_repository(request)
    _require_scoped_list_permission(request, "auditoria", "ler", cliente_id)
    filters = {
        "user_id": user_id,
        "cliente_id": cliente_id,
        "recurso": recurso,
        "acao": acao,
        "status": status,
    }
    return AdminAccessAuditListResponse(
        items=repository.list_admin_access_audits(
            limit=limit,
            offset=offset,
            **filters,
        ),
        limit=limit,
        offset=offset,
        total=repository.count_admin_access_audits(**filters),
    )


@router.post(
    "/auditoria/retencao/executar",
    response_model=AuditRetentionResponse,
)
def execute_audit_retention(
    request: Request,
    dias: int = Query(default=180, ge=1, le=3650),
) -> AuditRetentionResponse:
    repository = _auth_repository(request)
    require_admin_permission(request, "auditoria", "administrar")
    cutoff = datetime.now(timezone.utc) - timedelta(days=dias)
    deleted_count = repository.delete_admin_access_audits_older_than(cutoff)
    return AuditRetentionResponse(
        retention_days=dias,
        deleted_count=deleted_count,
    )


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


@router.get("/clientes", response_model=ClienteListResponse)
def list_clientes(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ativo: bool | None = None,
) -> ClienteListResponse:
    repository = _core_repository(request)
    require_admin_permission(request, "clientes", "ler")
    return ClienteListResponse(
        items=repository.list_clientes(limit=limit, offset=offset, ativo=ativo),
        limit=limit,
        offset=offset,
        total=repository.count_clientes(ativo=ativo),
    )


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


@router.patch("/clientes/{cliente_id}", response_model=Cliente)
def update_cliente(
    cliente_id: str,
    payload: ClienteUpdateRequest,
    request: Request,
) -> Cliente:
    repository = _core_repository(request)
    current = repository.get_cliente(cliente_id)
    if current is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cliente nao encontrado")
    require_admin_permission(request, "clientes", "editar", cliente_id)
    updated = current.model_copy(
        update={
            "nome": payload.nome if payload.nome is not None else current.nome,
            "documento": (
                payload.documento
                if "documento" in payload.model_fields_set
                else current.documento
            ),
            "ativo": payload.ativo if payload.ativo is not None else current.ativo,
        }
    )
    repository.save_cliente(updated)
    return updated


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


@router.get("/dispositivos", response_model=DispositivoListResponse)
def list_dispositivos(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    cliente_id: str | None = None,
    bloqueado: bool | None = None,
) -> DispositivoListResponse:
    repository = _core_repository(request)
    _require_scoped_list_permission(request, "dispositivos", "ler", cliente_id)
    return DispositivoListResponse(
        items=repository.list_dispositivos(
            limit=limit,
            offset=offset,
            cliente_id=cliente_id,
            bloqueado=bloqueado,
        ),
        limit=limit,
        offset=offset,
        total=repository.count_dispositivos(
            cliente_id=cliente_id,
            bloqueado=bloqueado,
        ),
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


@router.patch("/dispositivos/{dispositivo_id}", response_model=Dispositivo)
def update_dispositivo(
    dispositivo_id: str,
    payload: DispositivoUpdateRequest,
    request: Request,
) -> Dispositivo:
    repository = _core_repository(request)
    current = repository.get_dispositivo(dispositivo_id)
    if current is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="dispositivo nao encontrado")
    require_admin_permission(request, "dispositivos", "editar", current.cliente_id)
    playlist_id = (
        payload.playlist_atual_id
        if "playlist_atual_id" in payload.model_fields_set
        else current.playlist_atual_id
    )
    if playlist_id is not None:
        playlist = repository.get_playlist(playlist_id)
        if playlist is None or playlist.cliente_id != current.cliente_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="playlist_id invalido")
    updated = current.model_copy(
        update={
            "nome": payload.nome if payload.nome is not None else current.nome,
            "codigo_ativacao": (
                payload.codigo_ativacao
                if payload.codigo_ativacao is not None
                else current.codigo_ativacao
            ),
            "bloqueado": (
                payload.bloqueado
                if payload.bloqueado is not None
                else current.bloqueado
            ),
            "playlist_atual_id": playlist_id,
        }
    )
    repository.save_dispositivo(updated)
    return updated


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


@router.get("/midias", response_model=MidiaListResponse)
def list_midias(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    cliente_id: str | None = None,
    ativo: bool | None = None,
) -> MidiaListResponse:
    repository = _core_repository(request)
    _require_scoped_list_permission(request, "midias", "ler", cliente_id)
    return MidiaListResponse(
        items=repository.list_midias(
            limit=limit,
            offset=offset,
            cliente_id=cliente_id,
            ativo=ativo,
        ),
        limit=limit,
        offset=offset,
        total=repository.count_midias(cliente_id=cliente_id, ativo=ativo),
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


@router.patch("/midias/{midia_id}", response_model=Midia)
def update_midia(
    midia_id: str,
    payload: MidiaUpdateRequest,
    request: Request,
) -> Midia:
    repository = _core_repository(request)
    current = repository.get_midia(midia_id)
    if current is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="midia nao encontrada")
    require_admin_permission(request, "midias", "editar", current.cliente_id)
    updated = current.model_copy(
        update={
            "nome": payload.nome if payload.nome is not None else current.nome,
            "duracao_segundos": (
                payload.duracao_segundos
                if "duracao_segundos" in payload.model_fields_set
                else current.duracao_segundos
            ),
            "ativo": payload.ativo if payload.ativo is not None else current.ativo,
        }
    )
    repository.save_midia(updated)
    return updated


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


@router.get("/playlists", response_model=PlaylistListResponse)
def list_playlists(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    cliente_id: str | None = None,
    ativa: bool | None = None,
) -> PlaylistListResponse:
    repository = _core_repository(request)
    _require_scoped_list_permission(request, "playlists", "ler", cliente_id)
    return PlaylistListResponse(
        items=repository.list_playlists(
            limit=limit,
            offset=offset,
            cliente_id=cliente_id,
            ativa=ativa,
        ),
        limit=limit,
        offset=offset,
        total=repository.count_playlists(cliente_id=cliente_id, ativa=ativa),
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


@router.patch("/playlists/{playlist_id}", response_model=Playlist)
def update_playlist(
    playlist_id: str,
    payload: PlaylistUpdateRequest,
    request: Request,
) -> Playlist:
    repository = _core_repository(request)
    current = repository.get_playlist(playlist_id)
    if current is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="playlist nao encontrada")
    require_admin_permission(request, "playlists", "editar", current.cliente_id)
    updated = current.model_copy(
        update={
            "nome": payload.nome if payload.nome is not None else current.nome,
            "ativa": payload.ativa if payload.ativa is not None else current.ativa,
            "versao": current.versao + 1,
        }
    )
    repository.save_playlist(updated)
    return updated


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


@router.get(
    "/playlists/{playlist_id}/midias",
    response_model=list[PlaylistMidia],
)
def list_playlist_midias(
    playlist_id: str,
    request: Request,
) -> list[PlaylistMidia]:
    repository = _core_repository(request)
    playlist = repository.get_playlist(playlist_id)
    if playlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="playlist nao encontrada")
    require_admin_permission(request, "playlists", "ler", playlist.cliente_id)
    return repository.list_playlist_midias(playlist_id)


@router.delete(
    "/playlists/{playlist_id}/midias/{midia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_midia_from_playlist(
    playlist_id: str,
    midia_id: str,
    request: Request,
) -> None:
    repository = _core_repository(request)
    playlist = repository.get_playlist(playlist_id)
    if playlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="playlist nao encontrada")
    require_admin_permission(request, "playlists", "editar", playlist.cliente_id)
    if not repository.remove_midia_from_playlist(playlist_id, midia_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vinculo nao encontrado")


@router.get(
    "/sincronizacoes",
    response_model=AdminSyncConfirmationListResponse,
)
def list_sync_confirmations(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    cliente_id: str | None = None,
    dispositivo_id: str | None = None,
    status_filtro: str | None = Query(default=None, alias="status"),
) -> AdminSyncConfirmationListResponse:
    repository = _core_repository(request)
    _require_scoped_list_permission(request, "sincronizacoes", "ler", cliente_id)
    filters = {
        "cliente_id": cliente_id,
        "dispositivo_id": dispositivo_id,
        "status": status_filtro,
    }
    return AdminSyncConfirmationListResponse(
        items=repository.list_sync_confirmations(
            limit=limit,
            offset=offset,
            **filters,
        ),
        limit=limit,
        offset=offset,
        total=repository.count_sync_confirmations(**filters),
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


def _auth_repository(request: Request):
    repository = getattr(request.app.state, "auth_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="repository indisponivel",
        )
    return repository


def _get_user_or_404(repository, user_id: str) -> UserAccount:
    user = repository.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="usuario nao encontrado",
        )
    return user


def _user_public(user: UserAccount) -> AdminUserPublic:
    return AdminUserPublic(
        id=user.id,
        nome=user.nome,
        email=user.email,
        perfil=user.perfil,
        ativo=user.ativo,
    )


def _require_scoped_list_permission(
    request: Request,
    recurso: str,
    acao: str,
    cliente_id: str | None,
) -> None:
    session = getattr(request.state, "admin_session", None)
    if session is not None and session.perfil not in {"admin", "super_admin"}:
        if cliente_id is None:
            record_admin_access(request, session, recurso, acao, "negado", cliente_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="cliente_id obrigatorio",
            )
    require_admin_permission(request, recurso, acao, cliente_id)
