from pydantic import BaseModel, Field


class Cliente(BaseModel):
    id: str = Field(min_length=1)
    nome: str = Field(min_length=1)
    documento: str | None = None
    ativo: bool = True


class ClienteCreateRequest(BaseModel):
    id: str | None = Field(default=None, min_length=1)
    nome: str = Field(min_length=1)
    documento: str | None = None
    ativo: bool = True


class ClienteListResponse(BaseModel):
    items: list[Cliente]
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class ClienteUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    documento: str | None = None
    ativo: bool | None = None


class Dispositivo(BaseModel):
    id: str = Field(min_length=1)
    cliente_id: str = Field(min_length=1)
    nome: str = Field(min_length=1)
    codigo_ativacao: str = Field(min_length=1)
    bloqueado: bool = False
    playlist_atual_id: str | None = None


class DispositivoCreateRequest(BaseModel):
    id: str | None = Field(default=None, min_length=1)
    cliente_id: str = Field(min_length=1)
    nome: str = Field(min_length=1)
    codigo_ativacao: str | None = Field(default=None, min_length=1)
    bloqueado: bool = False
    playlist_atual_id: str | None = None


class DispositivoListResponse(BaseModel):
    items: list[Dispositivo]
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class DispositivoUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    codigo_ativacao: str | None = Field(default=None, min_length=1)
    bloqueado: bool | None = None
    playlist_atual_id: str | None = None


class Midia(BaseModel):
    id: str = Field(min_length=1)
    cliente_id: str = Field(min_length=1)
    nome: str = Field(min_length=1)
    tipo: str = Field(min_length=1)
    caminho: str = Field(min_length=1)
    tamanho: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)
    duracao_segundos: int | None = Field(default=None, ge=0)
    ativo: bool = True


class MidiaListResponse(BaseModel):
    items: list[Midia]
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class MidiaUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    duracao_segundos: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class Playlist(BaseModel):
    id: str = Field(min_length=1)
    cliente_id: str = Field(min_length=1)
    nome: str = Field(min_length=1)
    versao: int = Field(default=1, ge=1)
    ativa: bool = False


class PlaylistListResponse(BaseModel):
    items: list[Playlist]
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class PlaylistUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    ativa: bool | None = None


class OperationalConfiguration(BaseModel):
    storage_provider: str
    max_upload_bytes: int = Field(ge=1)
    offline_first: bool


class PlaylistMidia(BaseModel):
    playlist_id: str = Field(min_length=1)
    midia_id: str = Field(min_length=1)
    ordem: int = Field(ge=1)
    duracao_override: int | None = Field(default=None, ge=0)


class PlaylistMidiaRequest(BaseModel):
    midia_id: str = Field(min_length=1)
    ordem: int = Field(ge=1)
    duracao_override: int | None = Field(default=None, ge=0)
