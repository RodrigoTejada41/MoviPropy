from datetime import datetime, timezone
from uuid import uuid4

import psycopg

from moviprogy_api.domain.google_drive import GoogleDriveFile, GoogleDriveFolder, GoogleDriveStatus


class PostgresGoogleDriveRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def save_oauth_state(self, state: str, user_id: str, expires_at: datetime) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO google_drive_oauth_states (state, user_id, expires_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (state)
                DO UPDATE SET user_id = EXCLUDED.user_id, expires_at = EXCLUDED.expires_at, used = FALSE
                """,
                (state, user_id, expires_at),
            )
            connection.commit()

    def consume_oauth_state(self, state: str) -> str | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT user_id
                FROM google_drive_oauth_states
                WHERE state = %s
                  AND used = FALSE
                  AND expires_at > NOW()
                """,
                (state,),
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                "UPDATE google_drive_oauth_states SET used = TRUE WHERE state = %s",
                (state,),
            )
            connection.commit()
        return str(row[0])

    def save_integration(
        self,
        connected_email: str,
        access_token_encrypted: str,
        refresh_token_encrypted: str,
        expires_at: datetime | None,
        status: str = "connected",
    ) -> str:
        integration_id = "google-drive"
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO integrations (
                    id,
                    type,
                    provider,
                    connected_email,
                    access_token_encrypted,
                    refresh_token_encrypted,
                    expires_at,
                    status
                )
                VALUES (%s, 'storage', 'google_drive', %s, %s, %s, %s, %s)
                ON CONFLICT (provider)
                DO UPDATE SET
                    connected_email = EXCLUDED.connected_email,
                    access_token_encrypted = EXCLUDED.access_token_encrypted,
                    refresh_token_encrypted = EXCLUDED.refresh_token_encrypted,
                    expires_at = EXCLUDED.expires_at,
                    status = EXCLUDED.status,
                    updated_at = NOW()
                """,
                (
                    integration_id,
                    connected_email,
                    access_token_encrypted,
                    refresh_token_encrypted,
                    expires_at,
                    status,
                ),
            )
            connection.commit()
        return integration_id

    def disconnect(self) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                UPDATE integrations
                SET status = 'disconnected', updated_at = NOW()
                WHERE provider = 'google_drive'
                """
            )
            connection.commit()

    def get_status(self) -> GoogleDriveStatus:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT
                    i.status,
                    i.connected_email,
                    i.created_at,
                    s.root_folder_id,
                    s.root_folder_name,
                    s.last_validation_at
                FROM integrations i
                LEFT JOIN google_drive_settings s ON s.integration_id = i.id
                WHERE i.provider = 'google_drive'
                """
            ).fetchone()
        if row is None or row[0] == "disconnected":
            return GoogleDriveStatus(connected=False, status="desconectado")
        return GoogleDriveStatus(
            connected=row[0] == "connected",
            status=row[0],
            email=row[1],
            connected_at=row[2],
            root_folder_id=row[3],
            root_folder_name=row[4],
            last_validation_at=row[5],
        )

    def save_root_folder(self, folder_id: str, folder_name: str) -> GoogleDriveFolder:
        with psycopg.connect(self._database_url) as connection:
            integration_row = connection.execute(
                "SELECT id FROM integrations WHERE provider = 'google_drive' AND status = 'connected'"
            ).fetchone()
            if integration_row is None:
                raise RuntimeError("google drive desconectado")
            connection.execute(
                """
                INSERT INTO google_drive_settings (
                    id,
                    integration_id,
                    root_folder_id,
                    root_folder_name,
                    last_validation_at,
                    status
                )
                VALUES ('google-drive-settings', %s, %s, %s, NOW(), 'ok')
                ON CONFLICT (id)
                DO UPDATE SET
                    integration_id = EXCLUDED.integration_id,
                    root_folder_id = EXCLUDED.root_folder_id,
                    root_folder_name = EXCLUDED.root_folder_name,
                    last_validation_at = NOW(),
                    status = 'ok',
                    updated_at = NOW()
                """,
                (integration_row[0], folder_id, folder_name),
            )
            connection.commit()
        return GoogleDriveFolder(id=folder_id, name=folder_name, status="ok")

    def save_client_folder(
        self,
        cliente_id: str,
        folder_id: str,
        folder_name: str,
    ) -> GoogleDriveFolder:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO client_storage_folders (
                    id,
                    cliente_id,
                    provider,
                    folder_id,
                    folder_name,
                    status
                )
                VALUES (%s, %s, 'google_drive', %s, %s, 'ok')
                ON CONFLICT (cliente_id, provider)
                DO UPDATE SET
                    folder_id = EXCLUDED.folder_id,
                    folder_name = EXCLUDED.folder_name,
                    status = 'ok',
                    updated_at = NOW()
                """,
                (f"gdrive-folder-{cliente_id}", cliente_id, folder_id, folder_name),
            )
            connection.commit()
        return GoogleDriveFolder(
            id=folder_id,
            name=folder_name,
            status="ok",
            cliente_id=cliente_id,
        )

    def list_folders(self) -> list[GoogleDriveFolder]:
        with psycopg.connect(self._database_url) as connection:
            root = connection.execute(
                """
                SELECT root_folder_id, root_folder_name, status
                FROM google_drive_settings
                WHERE root_folder_id IS NOT NULL
                """
            ).fetchall()
            client_rows = connection.execute(
                """
                SELECT folder_id, folder_name, status, cliente_id
                FROM client_storage_folders
                WHERE provider = 'google_drive'
                ORDER BY folder_name ASC
                """
            ).fetchall()
        folders = [
            GoogleDriveFolder(id=row[0], name=row[1], status=row[2])
            for row in root
        ]
        folders.extend(
            GoogleDriveFolder(
                id=row[0],
                name=row[1],
                status=row[2],
                cliente_id=row[3],
            )
            for row in client_rows
        )
        return folders

    def list_files(
        self,
        cliente_id: str | None = None,
        folder_id: str | None = None,
    ) -> list[GoogleDriveFile]:
        clauses = ["origem_armazenamento = 'google_drive'"]
        params: list[object] = []
        if cliente_id is not None:
            clauses.append("cliente_id = %s")
            params.append(cliente_id)
        if folder_id is not None:
            clauses.append("google_drive_folder_id = %s")
            params.append(folder_id)
        with psycopg.connect(self._database_url) as connection:
            rows = connection.execute(
                f"""
                SELECT
                    google_drive_file_id,
                    nome,
                    google_drive_mime_type,
                    tamanho,
                    updated_at,
                    google_drive_web_view_link,
                    status,
                    cliente_id
                FROM midias
                WHERE {" AND ".join(clauses)}
                ORDER BY nome ASC
                """,
                params,
            ).fetchall()
        return [
            GoogleDriveFile(
                id=row[0],
                name=row[1],
                mime_type=row[2],
                size=row[3],
                modified_at=row[4],
                web_view_link=row[5],
                import_status=row[6],
                cliente_id=row[7],
            )
            for row in rows
            if row[0] is not None
        ]

    def save_imported_media_metadata(
        self,
        midia_id: str,
        file_id: str,
        folder_id: str | None,
        mime_type: str | None,
        web_view_link: str | None,
    ) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                UPDATE midias
                SET
                    origem_armazenamento = 'google_drive',
                    google_drive_file_id = %s,
                    google_drive_folder_id = %s,
                    google_drive_mime_type = %s,
                    google_drive_web_view_link = %s,
                    status = 'disponivel',
                    imported_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (file_id, folder_id, mime_type, web_view_link, midia_id),
            )
            connection.commit()

    def validate_access(self) -> GoogleDriveStatus:
        status = self.get_status()
        if status.connected:
            with psycopg.connect(self._database_url) as connection:
                connection.execute(
                    """
                    UPDATE google_drive_settings
                    SET last_validation_at = NOW(), status = 'ok', updated_at = NOW()
                    WHERE id = 'google-drive-settings'
                    """
                )
                connection.commit()
            return self.get_status()
        return status

    def record_operation(
        self,
        operation: str,
        status: str,
        user_id: str | None = None,
        cliente_id: str | None = None,
        midia_id: str | None = None,
        message: str | None = None,
    ) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO google_drive_operations (
                    user_id,
                    cliente_id,
                    midia_id,
                    operation,
                    status,
                    message
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, cliente_id, midia_id, operation, status, message),
            )
            connection.commit()


def generated_folder_id(prefix: str = "gdrive-folder") -> str:
    return f"{prefix}-{uuid4().hex}"
