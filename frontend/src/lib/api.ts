import { getToken } from "./session";
import type {
  AdminAudit,
  Cliente,
  Dispositivo,
  LoginResponse,
  Midia,
  PageResult,
  Playlist,
  User
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    const message = detail?.detail ?? `Erro HTTP ${response.status}`;
    throw new ApiError(message, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  login(email: string, senha: string) {
    return request<LoginResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, senha })
    });
  },
  logout() {
    return request<{ status: string }>("/api/auth/logout", { method: "POST" });
  },
  refresh() {
    return request<LoginResponse>("/api/auth/refresh", { method: "POST" });
  },
  health() {
    return request<{ status: string }>("/health");
  },
  clientes() {
    return request<PageResult<Cliente>>("/api/admin/clientes?limit=50&offset=0");
  },
  criarCliente(payload: Cliente) {
    return request<Cliente>("/api/admin/clientes", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  dispositivos() {
    return request<PageResult<Dispositivo>>("/api/admin/dispositivos?limit=50&offset=0");
  },
  criarDispositivo(payload: Dispositivo) {
    return request<Dispositivo>("/api/admin/dispositivos", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  midias() {
    return request<PageResult<Midia>>("/api/admin/midias?limit=50&offset=0");
  },
  playlists() {
    return request<PageResult<Playlist>>("/api/admin/playlists?limit=50&offset=0");
  },
  usuarios() {
    return request<PageResult<User>>("/api/admin/usuarios?limit=50&offset=0");
  },
  auditoria() {
    return request<PageResult<AdminAudit>>("/api/admin/auditoria/acessos?limit=50&offset=0");
  }
};
