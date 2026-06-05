from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException, Request, status

from moviprogy_api.domain.auth import (
    AdminSession,
    LoginRequest,
    LoginResponse,
    UserPublic,
)
from moviprogy_api.security import (
    create_access_token,
    hash_token,
    verify_password,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request) -> LoginResponse:
    repository = getattr(request.app.state, "auth_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="auth repository indisponivel",
        )

    user = repository.get_user_by_email(payload.email)
    if user is None or not user.ativo or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="credenciais invalidas",
        )

    token = create_access_token()
    repository.save_session(
        hash_token(token),
        AdminSession(
            user_id=user.id,
            perfil=user.perfil,
            ativo=user.ativo,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=8),
        ),
    )
    return LoginResponse(
        access_token=token,
        usuario=UserPublic(
            id=user.id,
            nome=user.nome,
            email=user.email,
            perfil=user.perfil,
        ),
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh(
    request: Request,
    authorization: str | None = Header(default=None),
) -> LoginResponse:
    repository = _auth_repository(request)
    old_token = _require_bearer_token(authorization)
    old_token_hash = hash_token(old_token)
    session = repository.get_session(old_token_hash)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="token invalido",
        )
    user = repository.get_user_by_id(session.user_id)
    if user is None or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="token invalido",
        )

    new_token = create_access_token()
    repository.delete_session(old_token_hash)
    repository.save_session(
        hash_token(new_token),
        AdminSession(
            user_id=user.id,
            perfil=user.perfil,
            ativo=user.ativo,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=8),
        ),
    )
    return LoginResponse(
        access_token=new_token,
        usuario=UserPublic(
            id=user.id,
            nome=user.nome,
            email=user.email,
            perfil=user.perfil,
        ),
    )


@router.post("/logout")
def logout(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    repository = _auth_repository(request)
    token = _require_bearer_token(authorization)
    token_hash = hash_token(token)
    session = repository.get_session(token_hash)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="token invalido",
        )
    repository.delete_session(token_hash)
    return {"status": "logout efetuado"}


def _auth_repository(request: Request):
    repository = getattr(request.app.state, "auth_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="auth repository indisponivel",
        )
    return repository


def _require_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token ausente",
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token ausente",
        )
    return token
