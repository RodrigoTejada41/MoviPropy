from moviprogy_api.domain.devices import ActivationRequest, DeviceRegistry


def test_device_registry_persists_session_to_json_file(tmp_path):
    data_file = tmp_path / "device_registry.json"
    registry = DeviceRegistry(data_file=data_file)

    activation = registry.activate(
        ActivationRequest(
            activation_code="MOVI-DEMO-001",
            hardware_id="BOX-PERSIST-001",
            player_version="0.1.0",
        )
    )

    assert activation is not None
    restored_registry = DeviceRegistry(data_file=data_file)
    manifest = restored_registry.get_manifest(activation.token)

    assert manifest is not None
    assert manifest.playlist_id == "playlist-demo-001"


def test_device_registry_does_not_store_plain_token(tmp_path):
    data_file = tmp_path / "device_registry.json"
    registry = DeviceRegistry(data_file=data_file)

    activation = registry.activate(
        ActivationRequest(
            activation_code="MOVI-DEMO-001",
            hardware_id="BOX-PERSIST-002",
            player_version="0.1.0",
        )
    )

    assert activation is not None
    assert activation.token not in data_file.read_text(encoding="utf-8")


def test_device_registry_creates_parent_directory(tmp_path):
    data_file = tmp_path / "nested" / "registry.json"

    DeviceRegistry(data_file=data_file)

    assert data_file.exists()
