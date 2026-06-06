export type MediaType = "imagem" | "video";

export interface MediaFile {
  media_id: string | null;
  file_name: string;
  media_type: string | null;
  size: number;
  sha256: string;
  duration_seconds: number | null;
}

export interface PlaylistManifest {
  playlist_id: string;
  version: number;
  files: MediaFile[];
}

export interface DeviceSession {
  device_id: string;
  token: string;
  playlist_version: number;
  hardware_id: string;
}

export interface PlayerStorage {
  getActiveManifest(): Promise<PlaylistManifest | null>;
  promote(manifest: PlaylistManifest, media: Map<string, Blob>): Promise<void>;
}

export interface TelemetryItem {
  id?: number;
  endpoint: "/api/player/status" | "/api/player/logs" | "/api/player/sincronizacao/confirmar";
  payload: Record<string, unknown>;
  created_at: string;
}
