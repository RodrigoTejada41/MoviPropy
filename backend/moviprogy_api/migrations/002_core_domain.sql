CREATE TABLE IF NOT EXISTS clientes (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    documento TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dispositivos (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes (id),
    nome TEXT NOT NULL,
    codigo_ativacao TEXT NOT NULL UNIQUE,
    bloqueado BOOLEAN NOT NULL DEFAULT FALSE,
    playlist_atual_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dispositivos_cliente_id
    ON dispositivos (cliente_id);

CREATE TABLE IF NOT EXISTS midias (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes (id),
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    caminho TEXT NOT NULL,
    tamanho BIGINT NOT NULL,
    sha256 TEXT NOT NULL,
    duracao_segundos INTEGER,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_midias_cliente_id
    ON midias (cliente_id);

CREATE TABLE IF NOT EXISTS playlists (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes (id),
    nome TEXT NOT NULL,
    versao INTEGER NOT NULL DEFAULT 1,
    ativa BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_playlists_cliente_id
    ON playlists (cliente_id);

CREATE TABLE IF NOT EXISTS playlist_midias (
    playlist_id TEXT NOT NULL REFERENCES playlists (id) ON DELETE CASCADE,
    midia_id TEXT NOT NULL REFERENCES midias (id),
    ordem INTEGER NOT NULL,
    duracao_override INTEGER,
    PRIMARY KEY (playlist_id, midia_id)
);

CREATE INDEX IF NOT EXISTS idx_playlist_midias_playlist_id
    ON playlist_midias (playlist_id);
