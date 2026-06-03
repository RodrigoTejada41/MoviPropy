import os
import secrets
import hashlib
from hmac import compare_digest

from fastapi import Header, HTTPException, Request, status

from moviprogy_api.domain.auth import AdminSession


PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 240_000
_FULL_ACCESS_PROFILES = {"admin", "super_admin"}


def require_admin_token(authorization: str | None = Header(default=None)) -> None:
    configured_token = os.getenv("ADMIN_API_TOKEN")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token admin ausente",
        )

    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token admin ausente",
        )

    if not configured_token or not compare_digest(token, configured_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="token admin invalido",
        )


def require_admin_user(
    request: Request,
    authorization: str | None = Header(default=None),
) -> AdminSession | None:
    token = _require_bearer_token(authorization)
    repository = getattr(request.app.state, "auth_repository", None)
    if repository is None:
        require_admin_token(authorization)
        return None

    session = repository.get_session(hash_token(token))
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="token invalido",
        )
    if not session.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permissao insuficiente",
        )
    request.state.admin_session = session
    return session


def require_admin_permission(
    request: Request,
    recurso: str,
    acao: str,
    cliente_id: str | None = None,
) -> None:
    session = getattr(request.state, "admin_session", None)
    if session is None:
        if getattr(request.app.state, "auth_repository", None) is None:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permissao insuficiente",
        )
    if session.perfil in _FULL_ACCESS_PROFILES:
        return

    repository = getattr(request.app.state, "auth_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permissao insuficiente",
        )
    if cliente_id is not None and not repository.has_cliente_access(
        session.user_id,
        cliente_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permissao insuficiente",
        )
    if not repository.has_permission(session.user_id, recurso, acao, cliente_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="permissao insuficiente",
        )


def create_access_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = _pbkdf2(password, salt, PASSWORD_HASH_ITERATIONS)
    return (
        f"{PASSWORD_HASH_ALGORITHM}"
        f"${PASSWORD_HASH_ITERATIONS}"
        f"${salt}"
        f"${password_hash}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt, expected_hash = stored_hash.split("$", 3)
        iterations = int(iterations_raw)
    except ValueError:
        return False

    if algorithm != PASSWORD_HASH_ALGORITHM:
        return False

    actual_hash = _pbkdf2(password, salt, iterations)
    return compare_digest(actual_hash, expected_hash)


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        iterations,
    ).hex()


def _require_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token ausente",
        )
    token = _extract_bearer_token(authorization)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token ausente",
        )
    return token


def _extract_bearer_token(authorization: str) -> str | None:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token
