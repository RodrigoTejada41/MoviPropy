import "fake-indexeddb/auto";
import { beforeEach, describe, expect, test } from "vitest";
import { IndexedDbPlayerStorage } from "./storage";
import type { PlaylistManifest } from "./types";

const manifest: PlaylistManifest = {
  playlist_id: "playlist-2",
  version: 2,
  files: [
    {
      media_id: "media-1",
      file_name: "image.jpg",
      media_type: "imagem",
      size: 3,
      sha256: "a".repeat(64),
      duration_seconds: 5
    }
  ]
};

describe("IndexedDbPlayerStorage", () => {
  beforeEach(async () => {
    await new Promise<void>((resolve) => {
      const request = indexedDB.deleteDatabase("moviprogy-player-test");
      request.onsuccess = () => resolve();
      request.onerror = () => resolve();
      request.onblocked = () => resolve();
    });
  });

  test("persists device session and active playlist", async () => {
    const storage = new IndexedDbPlayerStorage("moviprogy-player-test");
    await storage.saveDevice({
      device_id: "device-1",
      token: "secret-token",
      playlist_version: 2,
      hardware_id: "hardware-1"
    });
    await storage.promote(manifest, new Map([["media-1", new Blob(["abc"])]]));

    expect(await storage.getDevice()).toMatchObject({ device_id: "device-1" });
    expect(await storage.getActiveManifest()).toEqual(manifest);
    expect((await storage.getMedia("media-1"))?.size).toBe(3);
  });

  test("promotes media as one active generation", async () => {
    const storage = new IndexedDbPlayerStorage("moviprogy-player-test");
    await storage.promote(manifest, new Map([["media-1", new Blob(["abc"])]]));
    await storage.promote(
      { ...manifest, playlist_id: "playlist-3", version: 3, files: [] },
      new Map()
    );

    expect((await storage.getActiveManifest())?.playlist_id).toBe("playlist-3");
    expect(await storage.getMedia("media-1")).toBeNull();
  });

  test("limits telemetry by removing the oldest events", async () => {
    const storage = new IndexedDbPlayerStorage("moviprogy-player-test", 2);
    for (const evento of ["one", "two", "three"]) {
      await storage.enqueueTelemetry({
        endpoint: "/api/player/logs",
        payload: { evento },
        created_at: evento
      });
    }

    const items = await storage.listTelemetry();
    expect(items.map((item) => item.payload.evento)).toEqual(["two", "three"]);
  });
});
