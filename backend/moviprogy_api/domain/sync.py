import hashlib
from pathlib import Path

from pydantic import BaseModel, Field


class MediaFile(BaseModel):
    file_name: str = Field(min_length=1)
    size: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)


class PlaylistManifest(BaseModel):
    playlist_id: str = Field(min_length=1)
    version: int = Field(ge=1)
    files: list[MediaFile]


class ManifestValidationResult(BaseModel):
    is_valid: bool
    errors: list[str]


def validate_manifest_files(
    manifest: PlaylistManifest,
    base_path: Path,
) -> ManifestValidationResult:
    errors: list[str] = []

    for media in manifest.files:
        file_path = base_path / media.file_name
        if not file_path.exists():
            errors.append(f"{media.file_name}: arquivo ausente")
            continue

        if file_path.stat().st_size != media.size:
            errors.append(f"{media.file_name}: tamanho invalido")
            continue

        if _sha256(file_path) != media.sha256:
            errors.append(f"{media.file_name}: hash invalido")

    return ManifestValidationResult(is_valid=not errors, errors=errors)


def _sha256(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
