from importlib import resources

import psycopg

from moviprogy_api.domain.devices import DeviceSession, DeviceSessionRepository


def run_migrations(database_url: str) -> None:
    migration_files = sorted(
        resources.files("moviprogy_api.migrations").glob("*.sql")
    )
    with psycopg.connect(database_url) as connection:
        for migration_file in migration_files:
            sql = migration_file.read_text(encoding="utf-8")
            connection.execute(sql)
        connection.commit()


class PostgresDeviceSessionRepository(DeviceSessionRepository):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def save_session(self, token_hash: str, session: DeviceSession) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO device_sessions (
                    token_hash,
                    device_id,
                    hardware_id,
                    player_version
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (token_hash)
                DO UPDATE SET
                    device_id = EXCLUDED.device_id,
                    hardware_id = EXCLUDED.hardware_id,
                    player_version = EXCLUDED.player_version,
                    updated_at = NOW()
                """,
                (
                    token_hash,
                    session.device_id,
                    session.hardware_id,
                    session.player_version,
                ),
            )
            connection.commit()

    def get_session(self, token_hash: str) -> DeviceSession | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT device_id, hardware_id, player_version
                FROM device_sessions
                WHERE token_hash = %s
                """,
                (token_hash,),
            ).fetchone()

        if row is None:
            return None

        device_id, hardware_id, player_version = row
        return DeviceSession(
            device_id=device_id,
            hardware_id=hardware_id,
            player_version=player_version,
        )
