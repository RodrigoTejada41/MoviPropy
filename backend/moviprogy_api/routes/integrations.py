from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from moviprogy_api.domain.core import Midia
from moviprogy_api.domain.google_drive import (
    GoogleDriveAuthorizationUrl,
    GoogleDriveClientFolderRequest,
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
from moviprogy_api.repositories.postgres_google_drive import generated_folder_id
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
    return _with_oauth_config(_google_repository(request).get_status())


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
    folder_id = payload.folder_id
    if folder_id is None and payload.create_if_missing:
        folder_id = generated_folder_id("gdrive-root")
    if folder_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="folder_id obrigatorio",
        )
    try:
        folder = _google_repository(request).save_root_folder(
            folder_id,
            payload.folder_name,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return folder


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
    folder_id = payload.folder_id or generated_folder_id("gdrive-client")
    folder_name = payload.folder_name or f"Cliente_{payload.cliente_id}"
    return _google_repository(request).save_client_folder(
        payload.cliente_id,
        folder_id,
        folder_name,
    )


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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="google drive desconectado",
        )
    midia = Midia(
        id=f"midia-{uuid4().hex}",
        cliente_id=payload.cliente_id,
        nome=payload.nome,
        tipo=payload.tipo,
        caminho=f"google_drive/{payload.file_id}",
        tamanho=payload.tamanho,
        sha256=payload.sha256,
    )
    core_repository.save_midia(midia)
    google_repository.save_imported_media_metadata(
        midia_id=midia.id,
        file_id=payload.file_id,
        folder_id=payload.folder_id,
        mime_type=payload.google_drive_mime_type,
        web_view_link=payload.google_drive_web_view_link,
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
