import type { PlaylistManifest } from "./types";

const supportedTypes = new Set(["imagem", "video"]);

export function validateManifest(manifest: PlaylistManifest): string[] {
  const errors: string[] = [];
  const mediaIds = new Set<string>();

  if (!manifest.playlist_id.trim()) errors.push("playlist_id ausente");
  if (!Number.isInteger(manifest.version) || manifest.version < 1) {
    errors.push("versao invalida");
  }

  for (const media of manifest.files) {
    if (!media.media_id) {
      errors.push(`media_id ausente: ${media.file_name}`);
    } else if (mediaIds.has(media.media_id)) {
      errors.push(`media_id duplicado: ${media.media_id}`);
    } else {
      mediaIds.add(media.media_id);
    }
    if (!supportedTypes.has(media.media_type ?? "")) {
      errors.push(`tipo de midia invalido: ${media.media_type ?? "ausente"}`);
    }
    if (media.size < 0) errors.push(`tamanho invalido: ${media.media_id ?? media.file_name}`);
    if (!/^[a-f0-9]{64}$/i.test(media.sha256)) {
      errors.push(`sha256 invalido: ${media.media_id ?? media.file_name}`);
    }
  }

  return errors;
}

export function nextMediaIndex(current: number, total: number): number {
  if (total <= 0) return 0;
  return (current + 1) % total;
}
