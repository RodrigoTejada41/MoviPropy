import os
from pathlib import Path

from fastapi import FastAPI

from moviprogy_api.database import get_database_url
from moviprogy_api.domain.devices import DeviceRegistry
from moviprogy_api.repositories.postgres_auth import PostgresAuthRepository
from moviprogy_api.repositories.postgres_core import PostgresCoreRepository
from moviprogy_api.repositories.postgres_devices import (
    PostgresDeviceSessionRepository,
    run_migrations,
)
from moviprogy_api.routes import admin, auth, health, player, system


def _device_registry_file() -> Path | None:
    data_dir = os.getenv("MOVIPROGY_DATA_DIR")
    if not data_dir:
        return None
    return Path(data_dir) / "device_registry.json"


def _media_dir() -> Path:
    return Path(os.getenv("MOVIPROGY_MEDIA_DIR", "runtime/media"))


def create_app() -> FastAPI:
    app = FastAPI(title="MoviProgy API", version="0.1.0")
    app.state.media_dir = _media_dir()
    database_url = get_database_url()
    if database_url:
        run_migrations(database_url)
        app.state.device_registry = DeviceRegistry(
            repository=PostgresDeviceSessionRepository(database_url)
        )
        app.state.core_repository = PostgresCoreRepository(database_url)
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
    return app


app = create_app()
