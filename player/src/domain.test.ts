import { describe, expect, test } from "vitest";
import { nextMediaIndex, validateManifest } from "./domain";
import type { PlaylistManifest } from "./types";

const manifest: PlaylistManifest = {
  playlist_id: "playlist-1",
  version: 2,
  files: [
    {
      media_id: "media-1",
      file_name: "one.jpg",
      media_type: "imagem",
      size: 3,
      sha256: "a".repeat(64),
      duration_seconds: 10
    },
    {
      media_id: "media-2",
      file_name: "two.mp4",
      media_type: "video",
      size: 4,
      sha256: "b".repeat(64),
      duration_seconds: null
    }
  ]
};

describe("validateManifest", () => {
  test("accepts a complete ordered manifest", () => {
    expect(validateManifest(manifest)).toEqual([]);
  });

  test("rejects duplicate media identifiers", () => {
    const invalid = {
      ...manifest,
      files: [manifest.files[0], manifest.files[0]]
    };

    expect(validateManifest(invalid)).toContain("media_id duplicado: media-1");
  });

  test("rejects unsupported media types", () => {
    const invalid = {
      ...manifest,
      files: [{ ...manifest.files[0], media_type: "pdf" }]
    };

    expect(validateManifest(invalid)).toContain("tipo de midia invalido: pdf");
  });
});

describe("nextMediaIndex", () => {
  test("advances and loops to the first item", () => {
    expect(nextMediaIndex(0, 2)).toBe(1);
    expect(nextMediaIndex(1, 2)).toBe(0);
  });

  test("returns zero for an empty playlist", () => {
    expect(nextMediaIndex(4, 0)).toBe(0);
  });
});
