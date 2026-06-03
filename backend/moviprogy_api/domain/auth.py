from datetime import datetime

from pydantic import BaseModel, Field


class UserAccount(BaseModel):
    id: str = Field(min_length=1)
    nome: str = Field(min_length=1)
    email: str = Field(min_length=3)
    senha_hash: str = Field(min_length=1)
    perfil: str = Field(min_length=1)
    ativo: bool = True


class UserPublic(BaseModel):
    id: str
    nome: str
    email: str = Field(min_length=3)
    perfil: str


class AdminSession(BaseModel):
    user_id: str
    perfil: str
    ativo: bool = True
    expires_at: datetime | None = None


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    senha: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UserPublic
