CREATE TABLE IF NOT EXISTS integrations (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    provider TEXT NOT NULL UNIQUE,
    connected_email TEXT,
    access_token_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT NOT NULL,
    expires_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS google_drive_settings (
    id TEXT PRIMARY KEY,
    integration_id TEXT NOT NULL REFERENCES integrations (id) ON DELETE CASCADE,
    root_folder_id TEXT,
    root_folder_name TEXT,
    last_validation_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_storage_folders (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes (id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    folder_id TEXT NOT NULL,
    folder_name TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (cliente_id, provider)
);

CREATE TABLE IF NOT EXISTS google_drive_oauth_states (
    state TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS google_drive_operations (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT,
    cliente_id TEXT,
    midia_id TEXT,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE midias
    ADD COLUMN IF NOT EXISTS origem_armazenamento TEXT NOT NULL DEFAULT 'local',
    ADD COLUMN IF NOT EXISTS google_drive_file_id TEXT,
    ADD COLUMN IF NOT EXISTS google_drive_folder_id TEXT,
    ADD COLUMN IF NOT EXISTS google_drive_mime_type TEXT,
    ADD COLUMN IF NOT EXISTS google_drive_web_view_link TEXT,
    ADD COLUMN IF NOT EXISTS google_drive_download_link TEXT,
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'disponivel',
    ADD COLUMN IF NOT EXISTS imported_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_integrations_provider ON integrations (provider);
CREATE INDEX IF NOT EXISTS idx_client_storage_folders_cliente ON client_storage_folders (cliente_id);
CREATE INDEX IF NOT EXISTS idx_midias_google_drive_file ON midias (google_drive_file_id);
