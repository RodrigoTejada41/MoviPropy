from datetime import datetime, timedelta, timezone
from uuid import uuid4
from urllib.parse import quote
from urllib.error import HTTPError

import psycopg

from moviprogy_api.domain.google_drive import GoogleDriveFile, GoogleDriveFolder, GoogleDriveStatus
from moviprogy_api.google_drive import (
    decrypt_secret,
    drive_api_request,
    drive_upload_request,
    encrypt_secret,
    google_oauth_simulated,
    refresh_access_token,
    token_expiration,
)


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

    def find_or_create_root_folder(self, folder_name: str) -> GoogleDriveFolder:
        status = self.get_status()
        if not status.connected:
            raise RuntimeError("google drive desconectado")
        existing = self._find_registered_root_folder(folder_name)
        if existing is not None and google_oauth_simulated():
            return existing
        if google_oauth_simulated():
            return GoogleDriveFolder(
                id=generated_folder_id("gdrive-root"),
                name=folder_name,
                status="ok",
            )
        token = self._valid_access_token()
        if existing is not None:
            verified = self._drive_folder_by_id(token, existing.id)
            if verified is not None:
                return verified
        escaped_name = folder_name.replace("'", "\\'")
        query = quote(
            "mimeType = 'application/vnd.google-apps.folder' "
            f"and name = '{escaped_name}' and trashed = false"
        )
        result = drive_api_request(token, f"/files?q={query}&fields=files(id,name)")
        files = result.get("files") or []
        if files:
            first = files[0]
            return GoogleDriveFolder(id=str(first["id"]), name=str(first["name"]), status="ok")
        created = drive_api_request(
            token,
            "/files?fields=id,name",
            method="POST",
            payload={
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            },
        )
        return GoogleDriveFolder(id=str(created["id"]), name=str(created["name"]), status="ok")

    def _drive_folder_by_id(self, token: str, folder_id: str) -> GoogleDriveFolder | None:
        try:
            payload = drive_api_request(
                token,
                f"/files/{folder_id}?fields=id,name,mimeType,trashed",
            )
        except HTTPError:
            return None
        if payload.get("trashed") is True:
            return None
        if payload.get("mimeType") != "application/vnd.google-apps.folder":
            return None
        return GoogleDriveFolder(id=str(payload["id"]), name=str(payload["name"]), status="ok")

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
        if folder_id is not None and cliente_id is None and self.get_status().connected and not google_oauth_simulated():
            return self._list_drive_files(folder_id)
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
                    google_drive_download_link,
                    status,
                    cliente_id,
                    google_drive_folder_id,
                    sha256
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
                download_link=row[6],
                import_status=row[7],
                cliente_id=row[8],
                folder_id=row[9],
                sha256=row[10],
            )
            for row in rows
            if row[0] is not None
        ]

    def _list_drive_files(self, folder_id: str) -> list[GoogleDriveFile]:
        token = self._valid_access_token()
        query = quote(f"'{folder_id}' in parents and trashed = false")
        fields = quote(
            "files(id,name,mimeType,size,modifiedTime,webViewLink,webContentLink,parents)"
        )
        payload = drive_api_request(token, f"/files?q={query}&fields={fields}")
        items = []
        for item in payload.get("files") or []:
            parents = item.get("parents") or []
            items.append(
                GoogleDriveFile(
                    id=str(item["id"]),
                    name=str(item["name"]),
                    mime_type=item.get("mimeType"),
                    size=int(item["size"]) if item.get("size") is not None else None,
                    modified_at=_parse_google_datetime(item.get("modifiedTime")),
                    web_view_link=item.get("webViewLink"),
                    download_link=item.get("webContentLink"),
                    import_status="disponivel",
                    folder_id=str(parents[0]) if parents else folder_id,
                )
            )
        return items

    def save_imported_media_metadata(
        self,
        midia_id: str,
        file_id: str,
        folder_id: str | None,
        mime_type: str | None,
        web_view_link: str | None,
        download_link: str | None = None,
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
                    google_drive_download_link = %s,
                    status = 'disponivel',
                    imported_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (file_id, folder_id, mime_type, web_view_link, download_link, midia_id),
            )
            connection.commit()

    def get_file_metadata(self, file_id: str) -> GoogleDriveFile:
        if google_oauth_simulated():
            return GoogleDriveFile(
                id=file_id,
                name=f"{file_id}.bin",
                mime_type="application/octet-stream",
                size=0,
                web_view_link=f"https://drive.google.com/file/d/{file_id}/view",
                download_link=f"https://drive.google.com/uc?id={file_id}&export=download",
                sha256="0" * 64,
            )
        token = self._valid_access_token()
        fields = ",".join(
            [
                "id",
                "name",
                "mimeType",
                "size",
                "modifiedTime",
                "webViewLink",
                "webContentLink",
                "parents",
            ]
        )
        payload = drive_api_request(token, f"/files/{file_id}?fields={fields}")
        parents = payload.get("parents") or []
        return GoogleDriveFile(
            id=str(payload["id"]),
            name=str(payload["name"]),
            mime_type=payload.get("mimeType"),
            size=int(payload["size"]) if payload.get("size") is not None else 0,
            modified_at=_parse_google_datetime(payload.get("modifiedTime")),
            web_view_link=payload.get("webViewLink"),
            download_link=payload.get("webContentLink"),
            sha256="0" * 64,
            folder_id=str(parents[0]) if parents else None,
        )

    def upload_file(
        self,
        folder_id: str,
        name: str,
        mime_type: str,
        content: bytes,
    ) -> GoogleDriveFile:
        if google_oauth_simulated():
            file_id = f"uploaded-{uuid4().hex}"
            return GoogleDriveFile(
                id=file_id,
                name=name,
                mime_type=mime_type,
                size=len(content),
                web_view_link=f"https://drive.google.com/file/d/{file_id}/view",
                download_link=f"https://drive.google.com/uc?id={file_id}&export=download",
                sha256="0" * 64,
                folder_id=folder_id,
            )
        token = self._valid_access_token()
        payload = drive_upload_request(
            token,
            {"name": name, "parents": [folder_id]},
            content,
            mime_type,
        )
        parents = payload.get("parents") or []
        return GoogleDriveFile(
            id=str(payload["id"]),
            name=str(payload["name"]),
            mime_type=payload.get("mimeType"),
            size=int(payload["size"]) if payload.get("size") is not None else len(content),
            modified_at=_parse_google_datetime(payload.get("modifiedTime")),
            web_view_link=payload.get("webViewLink"),
            download_link=payload.get("webContentLink"),
            folder_id=str(parents[0]) if parents else folder_id,
        )

    def validate_access(self) -> GoogleDriveStatus:
        status = self.get_status()
        if status.connected:
            quota = self._storage_quota()
            with psycopg.connect(self._database_url) as connection:
                connection.execute(
                    """
                    UPDATE google_drive_settings
                    SET last_validation_at = NOW(), status = 'ok', updated_at = NOW()
                    WHERE id = 'google-drive-settings'
                    """
                )
                connection.commit()
            refreshed = self.get_status()
            refreshed.storage_used_bytes = quota.get("used")
            refreshed.storage_limit_bytes = quota.get("limit")
            refreshed.storage_available_bytes = quota.get("available")
            refreshed.file_count = quota.get("file_count")
            return refreshed
        return status

    def _find_registered_root_folder(self, folder_name: str) -> GoogleDriveFolder | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT root_folder_id, root_folder_name, status
                FROM google_drive_settings
                WHERE root_folder_name = %s
                  AND root_folder_id IS NOT NULL
                """,
                (folder_name,),
            ).fetchone()
        if row is None:
            return None
        return GoogleDriveFolder(id=row[0], name=row[1], status=row[2])

    def _integration_tokens(self) -> tuple[str, str, datetime | None]:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT access_token_encrypted, refresh_token_encrypted, expires_at
                FROM integrations
                WHERE provider = 'google_drive' AND status = 'connected'
                """
            ).fetchone()
        if row is None:
            raise RuntimeError("google drive desconectado")
        return decrypt_secret(row[0]), decrypt_secret(row[1]), row[2]

    def _valid_access_token(self) -> str:
        access_token, refresh_token, expires_at = self._integration_tokens()
        if expires_at is None or expires_at > datetime.now(timezone.utc) + timedelta(minutes=2):
            return access_token
        tokens = refresh_access_token(refresh_token)
        new_access_token = str(tokens["access_token"])
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                UPDATE integrations
                SET access_token_encrypted = %s, expires_at = %s, updated_at = NOW()
                WHERE provider = 'google_drive'
                """,
                (encrypt_secret(new_access_token), token_expiration(tokens)),
            )
            connection.commit()
        return new_access_token

    def _storage_quota(self) -> dict[str, int | None]:
        if google_oauth_simulated():
            return {
                "used": 0,
                "limit": None,
                "available": None,
                "file_count": len(self.list_files()),
            }
        token = self._valid_access_token()
        about = drive_api_request(token, "/about?fields=storageQuota")
        quota = about.get("storageQuota") or {}
        used = int(quota["usage"]) if quota.get("usage") is not None else None
        limit = int(quota["limit"]) if quota.get("limit") is not None else None
        available = limit - used if limit is not None and used is not None else None
        return {
            "used": used,
            "limit": limit,
            "available": available,
            "file_count": len(self.list_files()),
        }

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


def _parse_google_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
