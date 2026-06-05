import { getToken } from "./session";
import type {
  AdminAudit,
  Cliente,
  Dispositivo,
  GoogleDriveFile,
  GoogleDriveFolder,
  GoogleDriveStatus,
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
  },
  googleDriveStatus() {
    return request<GoogleDriveStatus>("/api/integrations/google-drive/status");
  },
  googleDriveConnect() {
    return request<{ authorization_url: string; state: string }>("/api/integrations/google-drive/connect", { method: "POST" });
  },
  googleDriveDisconnect() {
    return request<{ status: string; message: string }>("/api/integrations/google-drive/disconnect", { method: "POST" });
  },
  googleDriveValidate() {
    return request<GoogleDriveStatus>("/api/integrations/google-drive/validate-access", {
      method: "POST",
      body: JSON.stringify({})
    });
  },
  googleDriveFolders() {
    return request<{ items: GoogleDriveFolder[] }>("/api/integrations/google-drive/folders");
  },
  googleDriveFiles(clienteId?: string) {
    const query = clienteId ? `?cliente_id=${encodeURIComponent(clienteId)}` : "";
    return request<{ items: GoogleDriveFile[] }>(`/api/integrations/google-drive/files${query}`);
  },
  googleDriveRootFolder(payload: { folder_id?: string | null; folder_name: string; create_if_missing: boolean }) {
    return request<GoogleDriveFolder>("/api/integrations/google-drive/root-folder", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  googleDriveClientFolder(payload: { cliente_id: string; folder_id?: string | null; folder_name?: string | null }) {
    return request<GoogleDriveFolder>("/api/integrations/google-drive/client-folder", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  googleDriveImportMedia(payload: {
    cliente_id: string;
    file_id: string;
    tipo: string;
    nome: string;
    tamanho: number;
    sha256: string;
    folder_id?: string | null;
    google_drive_mime_type?: string | null;
    google_drive_web_view_link?: string | null;
  }) {
    return request<Midia>("/api/integrations/google-drive/import-media", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }
};
