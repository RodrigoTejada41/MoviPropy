CREATE TABLE IF NOT EXISTS usuarios_clientes (
    usuario_id TEXT NOT NULL REFERENCES usuarios (id) ON DELETE CASCADE,
    cliente_id TEXT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (usuario_id, cliente_id)
);

CREATE INDEX IF NOT EXISTS idx_usuarios_clientes_cliente_id
    ON usuarios_clientes (cliente_id);

CREATE TABLE IF NOT EXISTS permissoes (
    id TEXT PRIMARY KEY,
    usuario_id TEXT NOT NULL REFERENCES usuarios (id) ON DELETE CASCADE,
    cliente_id TEXT,
    recurso TEXT NOT NULL,
    acao TEXT NOT NULL,
    permitido BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_permissoes_usuario_recurso_acao
    ON permissoes (usuario_id, recurso, acao);

CREATE INDEX IF NOT EXISTS idx_permissoes_cliente_id
    ON permissoes (cliente_id);
