import os
from dataclasses import dataclass

import psycopg


@dataclass(frozen=True)
class DatabaseStatus:
    configured: bool
    available: bool


def get_database_url() -> str | None:
    return os.getenv("DATABASE_URL")


def check_database(database_url: str | None = None) -> DatabaseStatus:
    url = database_url if database_url is not None else get_database_url()
    if not url:
        return DatabaseStatus(configured=False, available=False)

    try:
        with psycopg.connect(url, connect_timeout=1) as connection:
            connection.execute("SELECT 1").fetchone()
    except Exception:
        return DatabaseStatus(configured=True, available=False)

    return DatabaseStatus(configured=True, available=True)
