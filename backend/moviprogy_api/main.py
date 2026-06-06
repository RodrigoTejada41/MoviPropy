import os
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from moviprogy_api.database import get_database_url
from moviprogy_api.domain.devices import DeviceRegistry
from moviprogy_api.observability import StructuredRequestLoggingMiddleware
from moviprogy_api.repositories.postgres_auth import PostgresAuthRepository
from moviprogy_api.repositories.postgres_core import PostgresCoreRepository
from moviprogy_api.repositories.postgres_devices import (
    PostgresDeviceSessionRepository,
    run_migrations,
)
from moviprogy_api.repositories.postgres_google_drive import PostgresGoogleDriveRepository
from moviprogy_api.routes import admin, auth, health, integrations, player, system


def _device_registry_file() -> Path | None:
    data_dir = os.getenv("MOVIPROGY_DATA_DIR")
    if not data_dir:
        return None
    return Path(data_dir) / "device_registry.json"


def _media_dir() -> Path:
    return Path(os.getenv("MOVIPROGY_MEDIA_DIR", "runtime/media"))


def _tmp_dir() -> Path:
    return Path(os.getenv("MOVIPROGY_TMP_DIR", "runtime/tmp"))


def _max_upload_bytes() -> int:
    return int(os.getenv("MOVIPROGY_MAX_UPLOAD_BYTES", str(512 * 1024 * 1024)))


def _environment() -> str:
    return os.getenv("MOVIPROGY_ENVIRONMENT", "development").lower()


def _allowed_hosts() -> list[str]:
    raw_hosts = os.getenv("MOVIPROGY_ALLOWED_HOSTS", "*")
    return [host.strip() for host in raw_hosts.split(",") if host.strip()]


def create_app() -> FastAPI:
    production = _environment() == "production"
    app = FastAPI(
        title="MoviProgy API",
        version="0.1.0",
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=_allowed_hosts())
    app.add_middleware(StructuredRequestLoggingMiddleware)
    app.state.media_dir = _media_dir()
    app.state.tmp_dir = _tmp_dir()
    app.state.max_upload_bytes = _max_upload_bytes()
    database_url = get_database_url()
    if database_url:
        run_migrations(database_url)
        app.state.device_registry = DeviceRegistry(
            repository=PostgresDeviceSessionRepository(database_url)
        )
        app.state.core_repository = PostgresCoreRepository(database_url)
        app.state.google_drive_repository = PostgresGoogleDriveRepository(database_url)
        auth_repository = PostgresAuthRepository(database_url)
        app.state.auth_repository = auth_repository
        admin_email = os.getenv("MOVIPROGY_ADMIN_EMAIL")
        admin_password = os.getenv("MOVIPROGY_ADMIN_PASSWORD")
        if admin_email and admin_password:
            auth_repository.ensure_default_admin(admin_email, admin_password)
    else:
        app.state.device_registry = DeviceRegistry(data_file=_device_registry_file())
    app.include_router(health.router)
    app.include_router(system.router, prefix="/api/system", tags=["system"])
    app.include_router(auth.router)
    app.include_router(player.router)
    app.include_router(admin.router)
    app.include_router(integrations.router)
    return app


app = create_app()
