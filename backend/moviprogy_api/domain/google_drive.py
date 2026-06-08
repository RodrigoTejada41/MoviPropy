from datetime import datetime

from pydantic import BaseModel, Field


class GoogleDriveStatus(BaseModel):
    connected: bool
    status: str
    email: str | None = None
    root_folder_id: str | None = None
    root_folder_name: str | None = None
    last_validation_at: datetime | None = None
    connected_at: datetime | None = None
    oauth_configured: bool = False
    oauth_simulated: bool = False
    missing_config: list[str] = []
    storage_used_bytes: int | None = None
    storage_limit_bytes: int | None = None
    storage_available_bytes: int | None = None
    file_count: int | None = None


class GoogleDriveAuthorizationUrl(BaseModel):
    authorization_url: str
    state: str


class GoogleDriveRootFolderRequest(BaseModel):
    folder_id: str | None = None
    folder_name: str = Field(default="MoviProgy_Midias", min_length=1)
    create_if_missing: bool = True


class GoogleDriveClientFolderRequest(BaseModel):
    cliente_id: str = Field(min_length=1)
    folder_id: str | None = None
    folder_name: str | None = None


class GoogleDriveFolder(BaseModel):
    id: str
    name: str
    status: str = "ok"
    cliente_id: str | None = None


class GoogleDriveFolderList(BaseModel):
    items: list[GoogleDriveFolder]


class GoogleDriveFile(BaseModel):
    id: str
    media_id: str | None = None
    name: str
    mime_type: str | None = None
    size: int | None = Field(default=None, ge=0)
    modified_at: datetime | None = None
    web_view_link: str | None = None
    download_link: str | None = None
    sha256: str | None = None
    import_status: str = "importado"
    cliente_id: str | None = None
    folder_id: str | None = None


class GoogleDriveFileList(BaseModel):
    items: list[GoogleDriveFile]


class GoogleDriveImportMediaRequest(BaseModel):
    cliente_id: str = Field(min_length=1)
    file_id: str = Field(min_length=1)
    tipo: str = Field(min_length=1)
    nome: str | None = None
    tamanho: int | None = Field(default=None, ge=0)
    sha256: str | None = Field(default=None, min_length=64, max_length=64)
    folder_id: str | None = None
    google_drive_mime_type: str | None = None
    google_drive_web_view_link: str | None = None
    google_drive_download_link: str | None = None


class GoogleDriveValidationRequest(BaseModel):
    cliente_id: str | None = None
    folder_id: str | None = None
    file_id: str | None = None


class GoogleDriveDeleteMediaRequest(BaseModel):
    confirmacao: str = Field(min_length=1)


class GoogleDriveOperationResult(BaseModel):
    status: str
    message: str
