// @vitest-environment jsdom

import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";
import { clearSession, saveSession } from "./session";

describe("api client", () => {
  beforeEach(() => {
    clearSession();
    vi.restoreAllMocks();
  });

  it("sends bearer token on protected requests", async () => {
    saveSession("admin-token", {
      id: "admin",
      nome: "Admin",
      email: "admin@example.com",
      perfil: "admin"
    });
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], limit: 50, offset: 0, total: 0 }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );

    await api.clientes();

    const headers = new Headers(fetchMock.mock.calls[0][1]?.headers);
    expect(headers.get("Authorization")).toBe("Bearer admin-token");
  });

  it("does not send authorization when no session exists", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );

    await api.health();

    const headers = new Headers(fetchMock.mock.calls[0][1]?.headers);
    expect(headers.has("Authorization")).toBe(false);
  });

  it("maps backend details to ApiError", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Acesso negado" }), {
        status: 403,
        headers: { "Content-Type": "application/json" }
      })
    );

    await expect(api.clientes()).rejects.toEqual(
      expect.objectContaining({
        message: "Acesso negado",
        status: 403
      })
    );
  });

  it("handles successful responses without content", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(null, { status: 204 }));

    await expect(api.removerMidia("playlist-1", "midia-1")).resolves.toBeUndefined();
  });

  it("keeps multipart content type managed by the browser", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ id: "midia-1" }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );

    await api.uploadMidia({
      cliente_id: "cliente-1",
      tipo: "imagem",
      arquivo: new File(["content"], "image.png", { type: "image/png" })
    });

    const request = fetchMock.mock.calls[0][1];
    const headers = new Headers(request?.headers);
    expect(headers.has("Content-Type")).toBe(false);
    expect(request?.body).toBeInstanceOf(FormData);
  });
});
