import { describe, expect, test } from "vitest";
import { synchronizePlayer } from "./sync";
import type { MediaFile, PlayerStorage, PlaylistManifest } from "./types";

class MemoryStorage implements PlayerStorage {
  activeManifest: PlaylistManifest | null = {
    playlist_id: "old",
    version: 1,
    files: []
  };
  activeMedia = new Map<string, Blob>();

  async getActiveManifest() {
    return this.activeManifest;
  }

  async promote(manifest: PlaylistManifest, media: Map<string, Blob>) {
    this.activeManifest = manifest;
    this.activeMedia = media;
  }
}

const newManifest: PlaylistManifest = {
  playlist_id: "new",
  version: 2,
  files: [
    {
      media_id: "media-1",
      file_name: "one.jpg",
      media_type: "imagem",
      size: 3,
      sha256: "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
      duration_seconds: 5
    }
  ]
};

describe("synchronizePlayer", () => {
  test("promotes a manifest only after every media file is valid", async () => {
    const storage = new MemoryStorage();
    const result = await synchronizePlayer({
      manifest: newManifest,
      storage,
      download: async (_media: MediaFile) => new Blob(["abc"])
    });

    expect(result).toEqual({ status: "concluida", downloaded: ["media-1"] });
    expect(storage.activeManifest?.playlist_id).toBe("new");
    expect(storage.activeMedia.get("media-1")?.size).toBe(3);
  });

  test("preserves the active playlist when a downloaded file is invalid", async () => {
    const storage = new MemoryStorage();

    await expect(
      synchronizePlayer({
        manifest: newManifest,
        storage,
        download: async () => new Blob(["invalid"])
      })
    ).rejects.toThrow("tamanho invalido: media-1");

    expect(storage.activeManifest?.playlist_id).toBe("old");
    expect(storage.activeMedia.size).toBe(0);
  });
});
