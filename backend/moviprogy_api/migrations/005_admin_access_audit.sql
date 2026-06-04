CREATE TABLE IF NOT EXISTS auditoria_acessos (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    cliente_id TEXT,
    recurso TEXT NOT NULL,
    acao TEXT NOT NULL,
    status TEXT NOT NULL,
    ip TEXT,
    user_agent TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_acessos_user_id
    ON auditoria_acessos (user_id);

CREATE INDEX IF NOT EXISTS idx_auditoria_acessos_cliente_id
    ON auditoria_acessos (cliente_id);

CREATE INDEX IF NOT EXISTS idx_auditoria_acessos_criado_em
    ON auditoria_acessos (criado_em DESC);
