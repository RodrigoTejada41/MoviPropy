import os
import uuid

import pytest

from moviprogy_api.domain.core import Cliente, Dispositivo, Midia, Playlist
from moviprogy_api.domain.player_events import (
    PlayerLogEvent,
    PlayerStatusEvent,
    SyncConfirmation,
)
from moviprogy_api.repositories.postgres_core import PostgresCoreRepository
from moviprogy_api.repositories.postgres_devices import run_migrations


DATABASE_URL = os.getenv("DATABASE_URL")


pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL nao configurado",
)


def test_postgres_core_repository_persists_core_entities():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresCoreRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    cliente = Cliente(id=f"cliente-{suffix}", nome="Cliente Teste")
    playlist = Playlist(
        id=f"playlist-{suffix}",
        cliente_id=cliente.id,
        nome="Playlist Principal",
        ativa=True,
    )
    dispositivo = Dispositivo(
        id=f"device-{suffix}",
        cliente_id=cliente.id,
        nome="TV Entrada",
        codigo_ativacao=f"CODE-{suffix}",
        playlist_atual_id=playlist.id,
    )
    midia = Midia(
        id=f"midia-{suffix}",
        cliente_id=cliente.id,
        nome="Video Demo",
        tipo="video",
        caminho="media/demo.mp4",
        tamanho=10,
        sha256="a" * 64,
        duracao_segundos=30,
    )

    repository.save_cliente(cliente)
    repository.save_playlist(playlist)
    repository.save_dispositivo(dispositivo)
    repository.save_midia(midia)
    repository.add_midia_to_playlist(playlist.id, midia.id, ordem=1)

    assert repository.get_cliente(cliente.id) == cliente
    assert repository.get_dispositivo(dispositivo.id) == dispositivo
    assert repository.get_midia(midia.id) == midia
    assert repository.get_playlist(playlist.id) == playlist
    assert repository.get_dispositivo_by_activation_code(
        dispositivo.codigo_ativacao
    ) == dispositivo

    manifest = repository.get_playlist_manifest_for_device(dispositivo.id)
    assert manifest is not None
    assert manifest.playlist_id == playlist.id
    assert manifest.version == playlist.versao
    assert manifest.files[0].file_name == midia.caminho
    assert manifest.files[0].size == midia.tamanho
    assert manifest.files[0].sha256 == midia.sha256
    assert repository.get_downloadable_midia_for_device(
        dispositivo.id,
        midia.id,
    ) == midia
    assert repository.get_downloadable_midia_for_device(
        dispositivo.id,
        f"midia-invalida-{suffix}",
    ) is None
    assert cliente in repository.list_clientes(limit=10_000)
    assert dispositivo in repository.list_dispositivos(limit=10_000)
    assert midia in repository.list_midias(limit=10_000)
    assert playlist in repository.list_playlists(limit=10_000)


def test_postgres_core_repository_filters_and_paginates_admin_lists():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresCoreRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    cliente_a = Cliente(id=f"cliente-list-a-{suffix}", nome=f"A {suffix}")
    cliente_b = Cliente(id=f"cliente-list-b-{suffix}", nome=f"B {suffix}", ativo=False)
    playlist_a = Playlist(
        id=f"playlist-list-a-{suffix}",
        cliente_id=cliente_a.id,
        nome=f"A {suffix}",
        ativa=True,
    )
    playlist_b = Playlist(
        id=f"playlist-list-b-{suffix}",
        cliente_id=cliente_b.id,
        nome=f"B {suffix}",
        ativa=False,
    )
    dispositivo_a = Dispositivo(
        id=f"device-list-a-{suffix}",
        cliente_id=cliente_a.id,
        nome=f"A {suffix}",
        codigo_ativacao=f"LIST-A-{suffix}",
        bloqueado=False,
    )
    dispositivo_b = Dispositivo(
        id=f"device-list-b-{suffix}",
        cliente_id=cliente_b.id,
        nome=f"B {suffix}",
        codigo_ativacao=f"LIST-B-{suffix}",
        bloqueado=True,
    )
    midia_a = Midia(
        id=f"midia-list-a-{suffix}",
        cliente_id=cliente_a.id,
        nome=f"A {suffix}",
        tipo="video",
        caminho=f"media/a-{suffix}.mp4",
        tamanho=10,
        sha256="a" * 64,
        ativo=True,
    )
    midia_b = Midia(
        id=f"midia-list-b-{suffix}",
        cliente_id=cliente_b.id,
        nome=f"B {suffix}",
        tipo="video",
        caminho=f"media/b-{suffix}.mp4",
        tamanho=10,
        sha256="b" * 64,
        ativo=False,
    )

    repository.save_cliente(cliente_a)
    repository.save_cliente(cliente_b)
    repository.save_playlist(playlist_a)
    repository.save_playlist(playlist_b)
    repository.save_dispositivo(dispositivo_a)
    repository.save_dispositivo(dispositivo_b)
    repository.save_midia(midia_a)
    repository.save_midia(midia_b)

    inactive_clientes = repository.list_clientes(limit=1, offset=0, ativo=False)
    assert len(inactive_clientes) == 1
    assert inactive_clientes[0].ativo is False
    assert repository.list_dispositivos(
        cliente_id=cliente_b.id,
        bloqueado=True,
    ) == [dispositivo_b]
    assert repository.list_midias(cliente_id=cliente_b.id, ativo=False) == [midia_b]
    assert repository.list_playlists(cliente_id=cliente_b.id, ativa=False) == [
        playlist_b
    ]


def test_player_update_check_uses_postgres_playlist_version():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresCoreRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    cliente = Cliente(id=f"cliente-update-{suffix}", nome="Cliente Update")
    playlist = Playlist(
        id=f"playlist-update-{suffix}",
        cliente_id=cliente.id,
        nome="Playlist Update",
        versao=5,
        ativa=True,
    )
    dispositivo = Dispositivo(
        id=f"device-update-{suffix}",
        cliente_id=cliente.id,
        nome="TV Update",
        codigo_ativacao=f"UPDATE-{suffix}",
        playlist_atual_id=playlist.id,
    )
    repository.save_cliente(cliente)
    repository.save_playlist(playlist)
    repository.save_dispositivo(dispositivo)

    manifest = repository.get_playlist_manifest_for_device(dispositivo.id)

    assert manifest is not None
    assert manifest.version == 5


def test_postgres_core_repository_persists_player_events():
    assert DATABASE_URL is not None
    run_migrations(DATABASE_URL)
    repository = PostgresCoreRepository(DATABASE_URL)
    suffix = uuid.uuid4().hex
    cliente = Cliente(id=f"cliente-events-{suffix}", nome="Cliente Eventos")
    dispositivo = Dispositivo(
        id=f"device-events-{suffix}",
        cliente_id=cliente.id,
        nome="TV Eventos",
        codigo_ativacao=f"CODE-EVENTS-{suffix}",
    )
    repository.save_cliente(cliente)
    repository.save_dispositivo(dispositivo)

    repository.save_player_status(
        PlayerStatusEvent(
            device_id=dispositivo.id,
            status="online",
            playlist_atual="playlist-001",
            versao_player="0.1.0",
            espaco_livre=2048,
        )
    )
    repository.save_player_log(
        PlayerLogEvent(
            device_id=dispositivo.id,
            nivel="info",
            evento="download_concluido",
            dados={"midia_id": "midia-001"},
        )
    )
    repository.save_sync_confirmation(
        SyncConfirmation(
            device_id=dispositivo.id,
            playlist_id="playlist-001",
            versao=3,
            arquivos_baixados=["midia-001"],
            status="concluida",
        )
    )

    events = repository.get_player_events_for_device(dispositivo.id)
    assert events["status"][0]["status"] == "online"
    assert events["logs"][0]["evento"] == "download_concluido"
    assert events["sync"][0]["status"] == "concluida"
