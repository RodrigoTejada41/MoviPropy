CREATE TABLE IF NOT EXISTS player_status_events (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES dispositivos(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    playlist_atual TEXT,
    versao_player TEXT NOT NULL,
    espaco_livre BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_player_status_events_device_created
    ON player_status_events (device_id, created_at DESC);

CREATE TABLE IF NOT EXISTS player_log_events (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES dispositivos(id) ON DELETE CASCADE,
    nivel TEXT NOT NULL,
    evento TEXT NOT NULL,
    dados JSONB NOT NULL DEFAULT '{}'::jsonb,
    criado_em TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_player_log_events_device_created
    ON player_log_events (device_id, created_at DESC);

CREATE TABLE IF NOT EXISTS player_sync_confirmations (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL REFERENCES dispositivos(id) ON DELETE CASCADE,
    playlist_id TEXT NOT NULL,
    versao INTEGER NOT NULL,
    arquivos_baixados JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_player_sync_confirmations_device_created
    ON player_sync_confirmations (device_id, created_at DESC);
