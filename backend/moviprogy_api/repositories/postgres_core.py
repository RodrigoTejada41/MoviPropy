import json

import psycopg

from moviprogy_api.domain.core import Cliente, Dispositivo, Midia, Playlist
from moviprogy_api.domain.player_events import (
    PlayerLogEvent,
    PlayerStatusEvent,
    SyncConfirmation,
)
from moviprogy_api.domain.sync import MediaFile, PlaylistManifest


class PostgresCoreRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def save_cliente(self, cliente: Cliente) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO clientes (id, nome, documento, ativo)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    nome = EXCLUDED.nome,
                    documento = EXCLUDED.documento,
                    ativo = EXCLUDED.ativo,
                    updated_at = NOW()
                """,
                (cliente.id, cliente.nome, cliente.documento, cliente.ativo),
            )
            connection.commit()

    def get_cliente(self, cliente_id: str) -> Cliente | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT id, nome, documento, ativo
                FROM clientes
                WHERE id = %s
                """,
                (cliente_id,),
            ).fetchone()
        if row is None:
            return None
        return Cliente(id=row[0], nome=row[1], documento=row[2], ativo=row[3])

    def save_dispositivo(self, dispositivo: Dispositivo) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO dispositivos (
                    id,
                    cliente_id,
                    nome,
                    codigo_ativacao,
                    bloqueado,
                    playlist_atual_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    cliente_id = EXCLUDED.cliente_id,
                    nome = EXCLUDED.nome,
                    codigo_ativacao = EXCLUDED.codigo_ativacao,
                    bloqueado = EXCLUDED.bloqueado,
                    playlist_atual_id = EXCLUDED.playlist_atual_id,
                    updated_at = NOW()
                """,
                (
                    dispositivo.id,
                    dispositivo.cliente_id,
                    dispositivo.nome,
                    dispositivo.codigo_ativacao,
                    dispositivo.bloqueado,
                    dispositivo.playlist_atual_id,
                ),
            )
            connection.commit()

    def get_dispositivo(self, dispositivo_id: str) -> Dispositivo | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    cliente_id,
                    nome,
                    codigo_ativacao,
                    bloqueado,
                    playlist_atual_id
                FROM dispositivos
                WHERE id = %s
                """,
                (dispositivo_id,),
            ).fetchone()
        if row is None:
            return None
        return Dispositivo(
            id=row[0],
            cliente_id=row[1],
            nome=row[2],
            codigo_ativacao=row[3],
            bloqueado=row[4],
            playlist_atual_id=row[5],
        )

    def get_dispositivo_by_activation_code(
        self,
        activation_code: str,
    ) -> Dispositivo | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    cliente_id,
                    nome,
                    codigo_ativacao,
                    bloqueado,
                    playlist_atual_id
                FROM dispositivos
                WHERE codigo_ativacao = %s
                  AND bloqueado = FALSE
                """,
                (activation_code,),
            ).fetchone()
        if row is None:
            return None
        return Dispositivo(
            id=row[0],
            cliente_id=row[1],
            nome=row[2],
            codigo_ativacao=row[3],
            bloqueado=row[4],
            playlist_atual_id=row[5],
        )

    def save_midia(self, midia: Midia) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO midias (
                    id,
                    cliente_id,
                    nome,
                    tipo,
                    caminho,
                    tamanho,
                    sha256,
                    duracao_segundos,
                    ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    cliente_id = EXCLUDED.cliente_id,
                    nome = EXCLUDED.nome,
                    tipo = EXCLUDED.tipo,
                    caminho = EXCLUDED.caminho,
                    tamanho = EXCLUDED.tamanho,
                    sha256 = EXCLUDED.sha256,
                    duracao_segundos = EXCLUDED.duracao_segundos,
                    ativo = EXCLUDED.ativo,
                    updated_at = NOW()
                """,
                (
                    midia.id,
                    midia.cliente_id,
                    midia.nome,
                    midia.tipo,
                    midia.caminho,
                    midia.tamanho,
                    midia.sha256,
                    midia.duracao_segundos,
                    midia.ativo,
                ),
            )
            connection.commit()

    def get_midia(self, midia_id: str) -> Midia | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    cliente_id,
                    nome,
                    tipo,
                    caminho,
                    tamanho,
                    sha256,
                    duracao_segundos,
                    ativo
                FROM midias
                WHERE id = %s
                """,
                (midia_id,),
            ).fetchone()
        if row is None:
            return None
        return Midia(
            id=row[0],
            cliente_id=row[1],
            nome=row[2],
            tipo=row[3],
            caminho=row[4],
            tamanho=row[5],
            sha256=row[6],
            duracao_segundos=row[7],
            ativo=row[8],
        )

    def save_playlist(self, playlist: Playlist) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO playlists (id, cliente_id, nome, versao, ativa)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    cliente_id = EXCLUDED.cliente_id,
                    nome = EXCLUDED.nome,
                    versao = EXCLUDED.versao,
                    ativa = EXCLUDED.ativa,
                    updated_at = NOW()
                """,
                (
                    playlist.id,
                    playlist.cliente_id,
                    playlist.nome,
                    playlist.versao,
                    playlist.ativa,
                ),
            )
            connection.commit()

    def get_playlist(self, playlist_id: str) -> Playlist | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT id, cliente_id, nome, versao, ativa
                FROM playlists
                WHERE id = %s
                """,
                (playlist_id,),
            ).fetchone()
        if row is None:
            return None
        return Playlist(
            id=row[0],
            cliente_id=row[1],
            nome=row[2],
            versao=row[3],
            ativa=row[4],
        )

    def add_midia_to_playlist(
        self,
        playlist_id: str,
        midia_id: str,
        ordem: int,
        duracao_override: int | None = None,
    ) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO playlist_midias (
                    playlist_id,
                    midia_id,
                    ordem,
                    duracao_override
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (playlist_id, midia_id)
                DO UPDATE SET
                    ordem = EXCLUDED.ordem,
                    duracao_override = EXCLUDED.duracao_override
                """,
                (playlist_id, midia_id, ordem, duracao_override),
            )
            connection.commit()

    def get_playlist_manifest_for_device(
        self,
        device_id: str,
    ) -> PlaylistManifest | None:
        with psycopg.connect(self._database_url) as connection:
            playlist_row = connection.execute(
                """
                SELECT p.id, p.versao
                FROM dispositivos d
                JOIN playlists p ON p.id = d.playlist_atual_id
                WHERE d.id = %s
                  AND d.bloqueado = FALSE
                  AND p.ativa = TRUE
                """,
                (device_id,),
            ).fetchone()
            if playlist_row is None:
                return None
            media_rows = connection.execute(
                """
                SELECT m.caminho, m.tamanho, m.sha256
                FROM playlist_midias pm
                JOIN midias m ON m.id = pm.midia_id
                WHERE pm.playlist_id = %s
                  AND m.ativo = TRUE
                ORDER BY pm.ordem ASC
                """,
                (playlist_row[0],),
            ).fetchall()

        return PlaylistManifest(
            playlist_id=playlist_row[0],
            version=playlist_row[1],
            files=[
                MediaFile(file_name=row[0], size=row[1], sha256=row[2])
                for row in media_rows
            ],
        )

    def get_downloadable_midia_for_device(
        self,
        device_id: str,
        midia_id: str,
    ) -> Midia | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT
                    m.id,
                    m.cliente_id,
                    m.nome,
                    m.tipo,
                    m.caminho,
                    m.tamanho,
                    m.sha256,
                    m.duracao_segundos,
                    m.ativo
                FROM dispositivos d
                JOIN playlists p ON p.id = d.playlist_atual_id
                JOIN playlist_midias pm ON pm.playlist_id = p.id
                JOIN midias m ON m.id = pm.midia_id
                WHERE d.id = %s
                  AND d.bloqueado = FALSE
                  AND p.ativa = TRUE
                  AND m.ativo = TRUE
                  AND m.id = %s
                """,
                (device_id, midia_id),
            ).fetchone()
        if row is None:
            return None
        return Midia(
            id=row[0],
            cliente_id=row[1],
            nome=row[2],
            tipo=row[3],
            caminho=row[4],
            tamanho=row[5],
            sha256=row[6],
            duracao_segundos=row[7],
            ativo=row[8],
        )

    def save_player_status(self, event: PlayerStatusEvent) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO player_status_events (
                    device_id,
                    status,
                    playlist_atual,
                    versao_player,
                    espaco_livre
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    event.device_id,
                    event.status,
                    event.playlist_atual,
                    event.versao_player,
                    event.espaco_livre,
                ),
            )
            connection.commit()

    def save_player_log(self, event: PlayerLogEvent) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO player_log_events (
                    device_id,
                    nivel,
                    evento,
                    dados,
                    criado_em
                )
                VALUES (%s, %s, %s, %s::jsonb, %s)
                """,
                (
                    event.device_id,
                    event.nivel,
                    event.evento,
                    json.dumps(event.dados),
                    event.criado_em,
                ),
            )
            connection.commit()

    def save_sync_confirmation(self, confirmation: SyncConfirmation) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO player_sync_confirmations (
                    device_id,
                    playlist_id,
                    versao,
                    arquivos_baixados,
                    status
                )
                VALUES (%s, %s, %s, %s::jsonb, %s)
                """,
                (
                    confirmation.device_id,
                    confirmation.playlist_id,
                    confirmation.versao,
                    json.dumps(confirmation.arquivos_baixados),
                    confirmation.status,
                ),
            )
            connection.commit()

    def get_player_events_for_device(self, device_id: str) -> dict[str, list[dict]]:
        with psycopg.connect(self._database_url) as connection:
            status_rows = connection.execute(
                """
                SELECT status, playlist_atual, versao_player, espaco_livre
                FROM player_status_events
                WHERE device_id = %s
                ORDER BY created_at DESC
                """,
                (device_id,),
            ).fetchall()
            log_rows = connection.execute(
                """
                SELECT nivel, evento, dados
                FROM player_log_events
                WHERE device_id = %s
                ORDER BY created_at DESC
                """,
                (device_id,),
            ).fetchall()
            sync_rows = connection.execute(
                """
                SELECT playlist_id, versao, arquivos_baixados, status
                FROM player_sync_confirmations
                WHERE device_id = %s
                ORDER BY created_at DESC
                """,
                (device_id,),
            ).fetchall()
        return {
            "status": [
                {
                    "status": row[0],
                    "playlist_atual": row[1],
                    "versao_player": row[2],
                    "espaco_livre": row[3],
                }
                for row in status_rows
            ],
            "logs": [
                {"nivel": row[0], "evento": row[1], "dados": row[2]}
                for row in log_rows
            ],
            "sync": [
                {
                    "playlist_id": row[0],
                    "versao": row[1],
                    "arquivos_baixados": row[2],
                    "status": row[3],
                }
                for row in sync_rows
            ],
        }
