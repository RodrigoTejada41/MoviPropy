ALTER TABLE client_storage_folders
    ADD COLUMN IF NOT EXISTS folder_type TEXT NOT NULL DEFAULT 'root';

ALTER TABLE midias
    ADD COLUMN IF NOT EXISTS google_drive_modified_at TIMESTAMPTZ;

ALTER TABLE client_storage_folders
    DROP CONSTRAINT IF EXISTS client_storage_folders_cliente_id_provider_key;

CREATE UNIQUE INDEX IF NOT EXISTS idx_client_storage_folders_cliente_provider_type
    ON client_storage_folders (cliente_id, provider, folder_type);

CREATE INDEX IF NOT EXISTS idx_client_storage_folders_folder_type
    ON client_storage_folders (cliente_id, folder_type);
