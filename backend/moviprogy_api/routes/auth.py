from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, status

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
