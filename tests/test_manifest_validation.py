import hashlib

from moviprogy_api.domain.sync import MediaFile, PlaylistManifest, validate_manifest_files


def test_manifest_is_valid_when_all_files_match_size_and_hash(tmp_path):
    video = tmp_path / "video.mp4"
    content = b"valid-video"
    video.write_bytes(content)

    manifest = PlaylistManifest(
        playlist_id="pl-001",
        version=1,
        files=[
            MediaFile(
                file_name="video.mp4",
                size=len(content),
                sha256=hashlib.sha256(content).hexdigest(),
            )
        ],
    )

    result = validate_manifest_files(manifest, tmp_path)

    assert result.is_valid is True
    assert result.errors == []


def test_manifest_is_invalid_when_file_is_missing(tmp_path):
    manifest = PlaylistManifest(
        playlist_id="pl-001",
        version=1,
        files=[
            MediaFile(
                file_name="missing.mp4",
                size=10,
                sha256="0" * 64,
            )
        ],
    )

    result = validate_manifest_files(manifest, tmp_path)

    assert result.is_valid is False
    assert result.errors == ["missing.mp4: arquivo ausente"]


def test_manifest_is_invalid_when_hash_does_not_match(tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"corrupted")

    manifest = PlaylistManifest(
        playlist_id="pl-001",
        version=1,
        files=[
            MediaFile(
                file_name="image.png",
                size=9,
                sha256="0" * 64,
            )
        ],
    )

    result = validate_manifest_files(manifest, tmp_path)

    assert result.is_valid is False
    assert result.errors == ["image.png: hash invalido"]
