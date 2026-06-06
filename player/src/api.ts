import type {
  DeviceSession,
  MediaFile,
  PlaylistManifest,
  TelemetryItem
} from "./types";

const PLAYER_VERSION = "0.1.0";

export class PlayerApi {
  async activate(activationCode: string, hardwareId: string): Promise<DeviceSession> {
    const response = await request<{
      device_id: string;
      token: string;
      playlist_version: number;
    }>("/api/player/ativar", {
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify({
        activation_code: activationCode,
        hardware_id: hardwareId,
        player_version: PLAYER_VERSION
      })
    });
    return { ...response, hardware_id: hardwareId };
  }

  checkUpdate(version: number, token: string): Promise<{
    possui_atualizacao: boolean;
    nova_versao: number;
  }> {
    return request(
      `/api/player/atualizacao?playlist_versao_atual=${encodeURIComponent(version)}`,
      { headers: bearerHeaders(token) }
    );
  }

  getManifest(token: string): Promise<PlaylistManifest> {
    return request("/api/player/playlist", { headers: bearerHeaders(token) });
  }

  async downloadMedia(mediaId: string, token: string): Promise<Blob> {
    const response = await fetch(
      `/api/player/midias/${encodeURIComponent(mediaId)}/download`,
      { headers: bearerHeaders(token) }
    );
    if (!response.ok) throw new Error(await responseError(response));
    return response.blob();
  }

  sendTelemetry(item: TelemetryItem, token: string): Promise<unknown> {
    return request(item.endpoint, {
      method: "POST",
      headers: { ...jsonHeaders(), ...bearerHeaders(token) },
      body: JSON.stringify(item.payload)
    });
  }
}

export function mediaId(media: MediaFile): string {
  if (!media.media_id) throw new Error(`media_id ausente: ${media.file_name}`);
  return media.media_id;
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(await responseError(response));
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function responseError(response: Response): Promise<string> {
  try {
    const body = await response.json() as { detail?: string };
    return body.detail || `falha HTTP ${response.status}`;
  } catch {
    return `falha HTTP ${response.status}`;
  }
}

function jsonHeaders(): Record<string, string> {
  return { "Content-Type": "application/json" };
}

function bearerHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` };
}
