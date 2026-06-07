import { getToken } from "./session";
import type {
  AdminAudit,
  Cliente,
  ClienteCreate,
  Dispositivo,
  DispositivoCreate,
  GoogleDriveFile,
  GoogleDriveFolder,
  GoogleDriveStatus,
  LoginResponse,
  Midia,
  OperationalConfiguration,
  PageResult,
  Permission,
  Playlist,
  PlaylistMidia,
  SyncConfirmation,
  User,
  UserClienteLink
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
  criarCliente(payload: ClienteCreate) {
    return request<Cliente>("/api/admin/clientes", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  atualizarCliente(id: string, payload: Partial<Pick<Cliente, "nome" | "documento" | "ativo">>) {
    return request<Cliente>(`/api/admin/clientes/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },
  dispositivos() {
    return request<PageResult<Dispositivo>>("/api/admin/dispositivos?limit=50&offset=0");
  },
  criarDispositivo(payload: DispositivoCreate) {
    return request<Dispositivo>("/api/admin/dispositivos", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  atualizarDispositivo(id: string, payload: Partial<Pick<Dispositivo, "nome" | "codigo_ativacao" | "bloqueado" | "playlist_atual_id">>) {
    return request<Dispositivo>(`/api/admin/dispositivos/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },
  midias() {
    return request<PageResult<Midia>>("/api/admin/midias?limit=50&offset=0");
  },
  uploadMidia(payload: { cliente_id: string; tipo: string; duracao_segundos?: number | null; arquivo: File }) {
    const body = new FormData();
    body.set("cliente_id", payload.cliente_id);
    body.set("tipo", payload.tipo);
    if (payload.duracao_segundos !== undefined && payload.duracao_segundos !== null) {
      body.set("duracao_segundos", String(payload.duracao_segundos));
    }
    body.set("arquivo", payload.arquivo);
    return request<Midia>("/api/admin/midias/upload", { method: "POST", body });
  },
  atualizarMidia(id: string, payload: Partial<Pick<Midia, "nome" | "duracao_segundos" | "ativo">>) {
    return request<Midia>(`/api/admin/midias/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },
  playlists() {
    return request<PageResult<Playlist>>("/api/admin/playlists?limit=50&offset=0");
  },
  criarPlaylist(payload: Playlist) {
    return request<Playlist>("/api/admin/playlists", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  atualizarPlaylist(id: string, payload: Partial<Pick<Playlist, "nome" | "ativa">>) {
    return request<Playlist>(`/api/admin/playlists/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },
  playlistMidias(id: string) {
    return request<PlaylistMidia[]>(`/api/admin/playlists/${encodeURIComponent(id)}/midias`);
  },
  vincularMidia(playlistId: string, payload: Omit<PlaylistMidia, "playlist_id">) {
    return request<PlaylistMidia>(`/api/admin/playlists/${encodeURIComponent(playlistId)}/midias`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  removerMidia(playlistId: string, midiaId: string) {
    return request<void>(`/api/admin/playlists/${encodeURIComponent(playlistId)}/midias/${encodeURIComponent(midiaId)}`, {
      method: "DELETE"
    });
  },
  sincronizacoes() {
    return request<PageResult<SyncConfirmation>>("/api/admin/sincronizacoes?limit=50&offset=0");
  },
  configuracoes() {
    return request<OperationalConfiguration>("/api/admin/configuracoes");
  },
  usuarios() {
    return request<PageResult<User>>("/api/admin/usuarios?limit=50&offset=0");
  },
  criarUsuario(payload: { id?: string; nome: string; email: string; senha: string; perfil: string; ativo: boolean }) {
    return request<User>("/api/admin/usuarios", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  atualizarUsuario(id: string, payload: Partial<Pick<User, "nome" | "email" | "perfil" | "ativo">> & { senha?: string }) {
    return request<User>(`/api/admin/usuarios/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },
  usuarioClientes(id: string) {
    return request<UserClienteLink[]>(`/api/admin/usuarios/${encodeURIComponent(id)}/clientes`);
  },
  vincularUsuarioCliente(id: string, payload: { cliente_id: string; ativo: boolean }) {
    return request<UserClienteLink>(`/api/admin/usuarios/${encodeURIComponent(id)}/clientes`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  usuarioPermissoes(id: string) {
    return request<Permission[]>(`/api/admin/usuarios/${encodeURIComponent(id)}/permissoes`);
  },
  concederPermissao(id: string, payload: { recurso: string; acao: string; cliente_id?: string | null; permitido: boolean }) {
    return request<Permission>(`/api/admin/usuarios/${encodeURIComponent(id)}/permissoes`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
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
  googleDriveFiles(filters: { clienteId?: string; folderId?: string } = {}) {
    const params = new URLSearchParams();
    if (filters.clienteId) params.set("cliente_id", filters.clienteId);
    if (filters.folderId) params.set("folder_id", filters.folderId);
    const query = params.toString() ? `?${params.toString()}` : "";
    return request<{ items: GoogleDriveFile[] }>(`/api/integrations/google-drive/files${query}`);
  },
  googleDriveRootFolder(payload: { folder_name: string }) {
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
  }) {
    return request<Midia>("/api/integrations/google-drive/import-media", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  googleDriveUploadMedia(payload: { cliente_id: string; tipo: string; arquivo: File }) {
    const formData = new FormData();
    formData.set("cliente_id", payload.cliente_id);
    formData.set("tipo", payload.tipo);
    formData.set("arquivo", payload.arquivo);
    return request<Midia>("/api/integrations/google-drive/upload-media", {
      method: "POST",
      body: formData
    });
  }
};
