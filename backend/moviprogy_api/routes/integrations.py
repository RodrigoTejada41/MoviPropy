from datetime import datetime, timedelta, timezone
import hashlib
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status

from moviprogy_api.domain.core import Midia
from moviprogy_api.domain.google_drive import (
    GoogleDriveAuthorizationUrl,
    GoogleDriveClientFolderRequest,
    GoogleDriveDeleteMediaRequest,
    GoogleDriveFileList,
    GoogleDriveFolder,
    GoogleDriveFolderList,
    GoogleDriveImportMediaRequest,
    GoogleDriveOperationResult,
    GoogleDriveRootFolderRequest,
    GoogleDriveStatus,
    GoogleDriveValidationRequest,
)
from moviprogy_api.google_drive import (
    GoogleDriveConfigError,
    build_authorization_url,
    connected_email,
    encrypt_secret,
    exchange_code_for_tokens,
    google_oauth_configured,
    google_oauth_simulated,
    missing_google_oauth_config,
    new_oauth_state,
    token_expiration,
)
from moviprogy_api.security import require_admin_permission, require_admin_user


router = APIRouter(
    prefix="/api/integrations/google-drive",
    tags=["integrations"],
)


@router.get("/status", response_model=GoogleDriveStatus)
def get_google_drive_status(
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveStatus:
    require_admin_permission(request, "integrations", "ler")
    repository = _google_repository(request)
    payload = repository.get_status()
    if payload.connected:
        payload = repository.validate_access()
    return _with_oauth_config(payload)


@router.post("/connect", response_model=GoogleDriveAuthorizationUrl)
def connect_google_drive(
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveAuthorizationUrl:
    require_admin_permission(request, "integrations", "administrar")
    state = new_oauth_state()
    try:
        authorization_url = build_authorization_url(state)
    except GoogleDriveConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    session = getattr(request.state, "admin_session", None)
    user_id = session.user_id if session is not None else "legacy-admin"
    _google_repository(request).save_oauth_state(
        state,
        user_id,
        datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    return GoogleDriveAuthorizationUrl(authorization_url=authorization_url, state=state)


@router.get("/callback", response_model=GoogleDriveOperationResult)
def google_drive_callback(
    request: Request,
    code: str = Query(min_length=1),
    state: str = Query(min_length=1),
) -> GoogleDriveOperationResult:
    repository = _google_repository(request)
    user_id = repository.consume_oauth_state(state)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="state oauth invalido",
        )
    try:
        tokens = exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        if not access_token or not refresh_token:
            raise GoogleDriveConfigError("tokens google incompletos")
        repository.save_integration(
            connected_email=connected_email(tokens),
            access_token_encrypted=encrypt_secret(str(access_token)),
            refresh_token_encrypted=encrypt_secret(str(refresh_token)),
            expires_at=token_expiration(tokens),
        )
        repository.record_operation(
            operation="connect",
            status="ok",
            user_id=user_id,
            message="Google Drive conectado",
        )
    except GoogleDriveConfigError as exc:
        repository.record_operation(
            operation="connect",
            status="erro",
            user_id=user_id,
            message=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return GoogleDriveOperationResult(
        status="ok",
        message="Google Drive conectado",
    )


@router.post("/disconnect", response_model=GoogleDriveOperationResult)
def disconnect_google_drive(
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveOperationResult:
    require_admin_permission(request, "integrations", "administrar")
    repository = _google_repository(request)
    repository.disconnect()
    repository.record_operation(
        operation="disconnect",
        status="ok",
        user_id=_user_id(request),
        message="Google Drive desconectado",
    )
    return GoogleDriveOperationResult(status="ok", message="Google Drive desconectado")


@router.get("/folders", response_model=GoogleDriveFolderList)
def list_google_drive_folders(
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveFolderList:
    require_admin_permission(request, "integrations", "ler")
    return GoogleDriveFolderList(items=_google_repository(request).list_folders())


@router.post("/root-folder", response_model=GoogleDriveFolder)
def set_google_drive_root_folder(
    payload: GoogleDriveRootFolderRequest,
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveFolder:
    require_admin_permission(request, "integrations", "administrar")
    repository = _google_repository(request)
    if not repository.get_status().connected:
        repository.record_operation(
            operation="root-folder",
            status="erro",
            user_id=_user_id(request),
            message="google drive desconectado",
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="google drive desconectado")
    try:
        if payload.folder_id:
            folder = GoogleDriveFolder(id=payload.folder_id, name=payload.folder_name, status="ok")
        else:
            folder = repository.find_or_create_root_folder(payload.folder_name)
        saved = repository.save_root_folder(folder.id, folder.name)
        repository.validate_access()
        repository.record_operation(
            operation="root-folder",
            status="ok",
            user_id=_user_id(request),
            message=saved.name,
        )
    except RuntimeError as exc:
        repository.record_operation(
            operation="root-folder",
            status="erro",
            user_id=_user_id(request),
            message=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return saved


@router.post("/client-folder", response_model=GoogleDriveFolder)
def set_google_drive_client_folder(
    payload: GoogleDriveClientFolderRequest,
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveFolder:
    core_repository = _core_repository(request)
    if core_repository.get_cliente(payload.cliente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cliente_id invalido",
        )
    require_admin_permission(
        request,
        "integrations",
        "administrar",
        payload.cliente_id,
    )
    google_repository = _google_repository(request)
    cliente = core_repository.get_cliente(payload.cliente_id)
    if payload.folder_id:
        folder_name = payload.folder_name or f"Cliente_{payload.cliente_id}"
        return google_repository.save_client_folder(
            payload.cliente_id,
            payload.folder_id,
            folder_name,
        )
    folders = google_repository.find_or_create_client_structure(
        payload.cliente_id,
        payload.folder_name or cliente.nome,
    )
    return folders[0]


@router.get("/files", response_model=GoogleDriveFileList)
def list_google_drive_files(
    request: Request,
    cliente_id: str | None = None,
    folder_id: str | None = None,
    _admin=Depends(require_admin_user),
) -> GoogleDriveFileList:
    if cliente_id is not None:
        require_admin_permission(request, "integrations", "ler", cliente_id)
    else:
        require_admin_permission(request, "integrations", "ler")
    return GoogleDriveFileList(
        items=_google_repository(request).list_files(
            cliente_id=cliente_id,
            folder_id=folder_id,
        )
    )


@router.post("/import-media", response_model=Midia, status_code=status.HTTP_201_CREATED)
def import_google_drive_media(
    payload: GoogleDriveImportMediaRequest,
    request: Request,
    _admin=Depends(require_admin_user),
) -> Midia:
    core_repository = _core_repository(request)
    google_repository = _google_repository(request)
    if core_repository.get_cliente(payload.cliente_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cliente_id invalido",
        )
    require_admin_permission(request, "midias", "criar", payload.cliente_id)
    if not google_repository.get_status().connected:
        google_repository.record_operation(
            operation="import-media",
            status="erro",
            user_id=_user_id(request),
            cliente_id=payload.cliente_id,
            message="google drive desconectado",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="google drive desconectado",
        )
    try:
        metadata = google_repository.get_file_metadata(payload.file_id)
    except RuntimeError as exc:
        google_repository.record_operation(
            operation="import-media",
            status="erro",
            user_id=_user_id(request),
            cliente_id=payload.cliente_id,
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    folder_id = payload.folder_id or metadata.folder_id
    if not google_repository.file_belongs_to_client(payload.cliente_id, folder_id):
        google_repository.record_operation(
            operation="import-media",
            status="erro",
            user_id=_user_id(request),
            cliente_id=payload.cliente_id,
            message="arquivo fora da pasta do cliente",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="arquivo fora da pasta do cliente",
        )
    midia = Midia(
        id=f"midia-{uuid4().hex}",
        cliente_id=payload.cliente_id,
        nome=payload.nome or metadata.name,
        tipo=payload.tipo,
        caminho=f"google_drive/{payload.file_id}",
        tamanho=payload.tamanho if payload.tamanho is not None else metadata.size or 0,
        sha256=payload.sha256 or metadata.sha256 or "0" * 64,
    )
    core_repository.save_midia(midia)
    google_repository.save_imported_media_metadata(
        midia_id=midia.id,
        file_id=payload.file_id,
        folder_id=folder_id,
        mime_type=payload.google_drive_mime_type or metadata.mime_type,
        web_view_link=payload.google_drive_web_view_link or metadata.web_view_link,
        download_link=payload.google_drive_download_link or metadata.download_link,
    )
    google_repository.record_operation(
        operation="import-media",
        status="ok",
        user_id=_user_id(request),
        cliente_id=payload.cliente_id,
        midia_id=midia.id,
        message=payload.file_id,
    )
    return midia


@router.post("/upload-media", response_model=Midia, status_code=status.HTTP_201_CREATED)
async def upload_google_drive_media(
    request: Request,
    cliente_id: str = Form(min_length=1),
    tipo: str = Form(min_length=1),
    arquivo: UploadFile = File(...),
    _admin=Depends(require_admin_user),
) -> Midia:
    core_repository = _core_repository(request)
    google_repository = _google_repository(request)
    if core_repository.get_cliente(cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cliente_id invalido")
    require_admin_permission(request, "midias", "criar", cliente_id)
    drive_status = google_repository.get_status()
    if not drive_status.connected:
        google_repository.record_operation(
            operation="upload-media",
            status="erro",
            user_id=_user_id(request),
            cliente_id=cliente_id,
            message="google drive desconectado",
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="google drive desconectado")
    if not drive_status.root_folder_id:
        google_repository.record_operation(
            operation="upload-media",
            status="erro",
            user_id=_user_id(request),
            cliente_id=cliente_id,
            message="pasta raiz nao definida",
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="pasta raiz nao definida")
    cliente = core_repository.get_cliente(cliente_id)
    folders = google_repository.find_or_create_client_structure(cliente_id, cliente.nome)
    target_folder_type = "videos" if tipo == "video" else "imagens"
    target_folder = google_repository.get_client_folder(cliente_id, target_folder_type)
    if target_folder is None:
        target_folder = next(
            (folder for folder in folders if folder.name.lower() == target_folder_type),
            folders[0],
        )
    content = await arquivo.read()
    filename = arquivo.filename or f"arquivo-{uuid4().hex}"
    mime_type = arquivo.content_type or "application/octet-stream"
    try:
        metadata = google_repository.upload_file(
            target_folder.id,
            filename,
            mime_type,
            content,
        )
    except RuntimeError as exc:
        google_repository.record_operation(
            operation="upload-media",
            status="erro",
            user_id=_user_id(request),
            cliente_id=cliente_id,
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    midia = Midia(
        id=f"midia-{uuid4().hex}",
        cliente_id=cliente_id,
        nome=metadata.name,
        tipo=tipo,
        caminho=f"google_drive/{metadata.id}",
        tamanho=metadata.size or len(content),
        sha256=metadata.sha256 or hashlib.sha256(content).hexdigest(),
    )
    core_repository.save_midia(midia)
    google_repository.save_imported_media_metadata(
        midia_id=midia.id,
        file_id=metadata.id,
        folder_id=metadata.folder_id or target_folder.id,
        mime_type=metadata.mime_type,
        web_view_link=metadata.web_view_link,
        download_link=metadata.download_link,
    )
    google_repository.record_operation(
        operation="upload-media",
        status="ok",
        user_id=_user_id(request),
        cliente_id=cliente_id,
        midia_id=midia.id,
        message=metadata.name,
    )
    return midia


@router.delete("/media/{midia_id}", response_model=GoogleDriveOperationResult)
def delete_google_drive_media(
    midia_id: str,
    payload: GoogleDriveDeleteMediaRequest,
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveOperationResult:
    if payload.confirmacao != "APAGAR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="confirmacao obrigatoria invalida",
        )
    core_repository = _core_repository(request)
    google_repository = _google_repository(request)
    midia = core_repository.get_midia(midia_id)
    if midia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="midia nao encontrada")
    require_admin_permission(request, "midias", "excluir", midia.cliente_id)
    metadata = google_repository.get_media_drive_metadata(midia_id)
    if metadata is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="midia nao vinculada ao google drive",
        )
    try:
        google_repository.delete_file(metadata.id)
    except RuntimeError as exc:
        google_repository.record_operation(
            operation="delete-media",
            status="erro",
            user_id=_user_id(request),
            cliente_id=midia.cliente_id,
            midia_id=midia.id,
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    core_repository.save_midia(midia.model_copy(update={"ativo": False}))
    google_repository.record_operation(
        operation="delete-media",
        status="ok",
        user_id=_user_id(request),
        cliente_id=midia.cliente_id,
        midia_id=midia.id,
        message=metadata.id,
    )
    return GoogleDriveOperationResult(status="ok", message="arquivo apagado do Google Drive")


@router.post("/validate-access", response_model=GoogleDriveStatus)
def validate_google_drive_access(
    payload: GoogleDriveValidationRequest,
    request: Request,
    _admin=Depends(require_admin_user),
) -> GoogleDriveStatus:
    require_admin_permission(request, "integrations", "ler", payload.cliente_id)
    return _with_oauth_config(_google_repository(request).validate_access())


def _google_repository(request: Request):
    repository = getattr(request.app.state, "google_drive_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="repository indisponivel",
        )
    return repository


def _core_repository(request: Request):
    repository = getattr(request.app.state, "core_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="repository indisponivel",
        )
    return repository


def _user_id(request: Request) -> str | None:
    session = getattr(request.state, "admin_session", None)
    return session.user_id if session is not None else None


def _with_oauth_config(payload: GoogleDriveStatus) -> GoogleDriveStatus:
    payload.oauth_configured = google_oauth_configured()
    payload.oauth_simulated = google_oauth_simulated()
    payload.missing_config = missing_google_oauth_config()
    return payload
