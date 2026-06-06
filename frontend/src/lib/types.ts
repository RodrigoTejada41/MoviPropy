export type User = {
  id: string;
  nome: string;
  email: string;
  perfil: string;
  ativo?: boolean;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  usuario: User;
};

export type PageResult<T> = {
  items: T[];
  limit: number;
  offset: number;
  total: number;
};

export type Cliente = {
  id: string;
  nome: string;
  documento?: string | null;
  ativo: boolean;
};

export type Dispositivo = {
  id: string;
  cliente_id: string;
  nome: string;
  codigo_ativacao: string;
  bloqueado: boolean;
  playlist_atual_id?: string | null;
};

export type Midia = {
  id: string;
  cliente_id: string;
  nome: string;
  tipo: string;
  caminho: string;
  tamanho: number;
  sha256: string;
  duracao_segundos?: number | null;
  ativo: boolean;
};

export type Playlist = {
  id: string;
  cliente_id: string;
  nome: string;
  versao: number;
  ativa: boolean;
};

export type AdminAudit = {
  user_id: string;
  recurso: string;
  acao: string;
  status: string;
  cliente_id?: string | null;
  ip?: string | null;
  user_agent?: string | null;
  created_at?: string | null;
};

export type GoogleDriveStatus = {
  connected: boolean;
  status: string;
  email?: string | null;
  root_folder_id?: string | null;
  root_folder_name?: string | null;
  last_validation_at?: string | null;
  connected_at?: string | null;
  oauth_configured: boolean;
  oauth_simulated: boolean;
  missing_config: string[];
  storage_used_bytes?: number | null;
  storage_limit_bytes?: number | null;
  storage_available_bytes?: number | null;
  file_count?: number | null;
};

export type GoogleDriveFolder = {
  id: string;
  name: string;
  status: string;
  cliente_id?: string | null;
};

export type GoogleDriveFile = {
  id: string;
  name: string;
  mime_type?: string | null;
  size?: number | null;
  modified_at?: string | null;
  web_view_link?: string | null;
  download_link?: string | null;
  folder_id?: string | null;
  sha256?: string | null;
  import_status: string;
  cliente_id?: string | null;
};
