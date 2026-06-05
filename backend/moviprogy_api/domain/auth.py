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


class AdminUserPublic(UserPublic):
    ativo: bool = True


class AdminUserListResponse(BaseModel):
    items: list[AdminUserPublic]
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class AdminUserCreateRequest(BaseModel):
    id: str | None = Field(default=None, min_length=1)
    nome: str = Field(min_length=1)
    email: str = Field(min_length=3)
    senha: str = Field(min_length=8)
    perfil: str = Field(min_length=1)
    ativo: bool = True


class AdminUserUpdateRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=3)
    senha: str | None = Field(default=None, min_length=8)
    perfil: str | None = Field(default=None, min_length=1)
    ativo: bool | None = None


class UserClienteLinkRequest(BaseModel):
    cliente_id: str = Field(min_length=1)
    ativo: bool = True


class UserClienteLink(BaseModel):
    user_id: str
    cliente_id: str
    ativo: bool = True


class PermissionGrantRequest(BaseModel):
    recurso: str = Field(min_length=1)
    acao: str = Field(min_length=1)
    cliente_id: str | None = Field(default=None, min_length=1)
    permitido: bool = True


class PermissionPublic(BaseModel):
    id: str
    user_id: str
    recurso: str
    acao: str
    cliente_id: str | None = None
    permitido: bool = True


class AdminSession(BaseModel):
    user_id: str
    perfil: str
    ativo: bool = True
    expires_at: datetime | None = None


class AdminAccessAudit(BaseModel):
    user_id: str
    recurso: str
    acao: str
    status: str
    cliente_id: str | None = None
    ip: str | None = None
    user_agent: str | None = None
    created_at: datetime | None = None


class AdminAccessAuditListResponse(BaseModel):
    items: list[AdminAccessAudit]
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    senha: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UserPublic
