import os
import uuid

import pytest

from moviprogy_api.domain.core import Cliente, Dispositivo, Midia, Playlist
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
