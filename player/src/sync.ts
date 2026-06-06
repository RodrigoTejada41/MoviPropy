import { validateManifest } from "./domain";
import type { MediaFile, PlayerStorage, PlaylistManifest } from "./types";

interface SynchronizeOptions {
  manifest: PlaylistManifest;
  storage: PlayerStorage;
  download(media: MediaFile): Promise<Blob>;
}

export async function synchronizePlayer({
  manifest,
  storage,
  download
}: SynchronizeOptions): Promise<{ status: "concluida"; downloaded: string[] }> {
  const errors = validateManifest(manifest);
  if (errors.length) throw new Error(errors.join("; "));

  const pending = new Map<string, Blob>();
  const downloaded: string[] = [];

  for (const media of manifest.files) {
    const mediaId = media.media_id as string;
    const blob = await download(media);
    if (blob.size !== media.size) throw new Error(`tamanho invalido: ${mediaId}`);
    const digest = await sha256(blob);
    if (digest !== media.sha256.toLowerCase()) throw new Error(`hash invalido: ${mediaId}`);
    pending.set(mediaId, blob);
    downloaded.push(mediaId);
  }

  await storage.promote(manifest, pending);
  return { status: "concluida", downloaded };
}

async function sha256(blob: Blob): Promise<string> {
  const buffer = await blob.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}
