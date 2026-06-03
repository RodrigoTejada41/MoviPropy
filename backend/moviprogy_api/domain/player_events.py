from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PlayerStatusPayload(BaseModel):
    status: str = Field(min_length=1)
    playlist_atual: str | None = None
    versao_player: str = Field(min_length=1)
    espaco_livre: int | None = Field(default=None, ge=0)


class PlayerStatusEvent(PlayerStatusPayload):
    device_id: str = Field(min_length=1)


class PlayerLogPayload(BaseModel):
    nivel: str = Field(min_length=1)
    evento: str = Field(min_length=1)
    dados: dict[str, Any] = Field(default_factory=dict)
    criado_em: datetime | None = None


class PlayerLogEvent(PlayerLogPayload):
    device_id: str = Field(min_length=1)


class SyncConfirmationPayload(BaseModel):
    playlist_id: str = Field(min_length=1)
    versao: int = Field(ge=1)
    arquivos_baixados: list[str] = Field(default_factory=list)
    status: str = Field(min_length=1)


class SyncConfirmation(SyncConfirmationPayload):
    device_id: str = Field(min_length=1)
