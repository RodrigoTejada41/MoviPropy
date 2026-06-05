import base64
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest, urlopen

from cryptography.fernet import Fernet


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"


class GoogleDriveConfigError(RuntimeError):
    pass


def google_oauth_configured() -> bool:
    return bool(
        os.getenv("MOVIPROGY_GOOGLE_CLIENT_ID")
        and os.getenv("MOVIPROGY_GOOGLE_CLIENT_SECRET")
        and os.getenv("MOVIPROGY_GOOGLE_REDIRECT_URI")
    )


def build_authorization_url(state: str) -> str:
    client_id = os.getenv("MOVIPROGY_GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("MOVIPROGY_GOOGLE_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise GoogleDriveConfigError("google oauth nao configurado")
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_DRIVE_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_code_for_tokens(code: str) -> dict:
    if os.getenv("MOVIPROGY_GOOGLE_OAUTH_SIMULATED", "").lower() == "true":
        return {
            "access_token": "simulated-access-token",
            "refresh_token": "simulated-refresh-token",
            "expires_in": 3600,
            "email": os.getenv(
                "MOVIPROGY_GOOGLE_SIMULATED_EMAIL",
                "simulado@moviprogy.local",
            ),
        }

    client_id = os.getenv("MOVIPROGY_GOOGLE_CLIENT_ID")
    client_secret = os.getenv("MOVIPROGY_GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("MOVIPROGY_GOOGLE_REDIRECT_URI")
    if not client_id or not client_secret or not redirect_uri:
        raise GoogleDriveConfigError("google oauth nao configurado")

    payload = urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    request = UrlRequest(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def encrypt_secret(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def token_expiration(tokens: dict) -> datetime | None:
    expires_in = tokens.get("expires_in")
    if expires_in is None:
        return None
    return datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))


def connected_email(tokens: dict) -> str:
    return str(tokens.get("email") or os.getenv("MOVIPROGY_GOOGLE_CONNECTED_EMAIL") or "conta-google-nao-informada")


def new_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def _fernet() -> Fernet:
    secret = os.getenv("MOVIPROGY_GOOGLE_TOKEN_KEY")
    if not secret:
        raise GoogleDriveConfigError("chave de criptografia google drive ausente")
    key = base64.urlsafe_b64encode(secret.encode("utf-8").ljust(32, b"0")[:32])
    return Fernet(key)

