import os
import uuid

import pytest

from moviprogy_api.domain.devices import DeviceSession
from moviprogy_api.repositories.postgres_devices import (
    PostgresDeviceSessionRepository,
    run_migrations,
)


DATABASE_URL = os.getenv("DATABASE_URL")


pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL nao configurado",
)


def test_postgres_repository_persists_and_loads_session():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresDeviceSessionRepository(DATABASE_URL)
    token_hash = f"test-{uuid.uuid4().hex}"

    repository.save_session(
        token_hash,
        DeviceSession(
            device_id="device-demo-001",
            hardware_id="BOX-PG-001",
            player_version="0.1.0",
        ),
    )

    session = repository.get_session(token_hash)

    assert session == DeviceSession(
        device_id="device-demo-001",
        hardware_id="BOX-PG-001",
        player_version="0.1.0",
    )


def test_run_migrations_is_idempotent():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    run_migrations(DATABASE_URL)
