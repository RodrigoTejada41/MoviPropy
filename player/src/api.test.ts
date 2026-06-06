import { afterEach, describe, expect, test, vi } from "vitest";
import { PlayerApi } from "./api";

describe("PlayerApi", () => {
  afterEach(() => vi.unstubAllGlobals());

  test("activates a device using the backend contract", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          device_id: "device-1",
          token: "token-1",
          playlist_version: 1
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );
    vi.stubGlobal("fetch", fetchMock);

    const api = new PlayerApi();
    const result = await api.activate("CODE-1", "hardware-1");

    expect(result.device_id).toBe("device-1");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/player/ativar",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          activation_code: "CODE-1",
          hardware_id: "hardware-1",
          player_version: "0.1.0"
        })
      })
    );
  });

  test("downloads media with the device bearer token", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response("abc", { status: 200 })
    );
    vi.stubGlobal("fetch", fetchMock);

    const api = new PlayerApi();
    const blob = await api.downloadMedia("media-1", "token-1");

    expect(blob.size).toBe(3);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/player/midias/media-1/download",
      expect.objectContaining({
        headers: { Authorization: "Bearer token-1" }
      })
    );
  });

  test("returns backend error detail without exposing request secrets", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "codigo de ativacao invalido" }), {
          status: 401,
          headers: { "Content-Type": "application/json" }
        })
      )
    );

    const api = new PlayerApi();
    await expect(api.activate("INVALID", "hardware-1")).rejects.toThrow(
      "codigo de ativacao invalido"
    );
  });
});
