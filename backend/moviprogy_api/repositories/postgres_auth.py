from datetime import datetime, timezone
from uuid import uuid4

import psycopg

from moviprogy_api.domain.auth import AdminAccessAudit, AdminSession, UserAccount
from moviprogy_api.security import hash_password


class PostgresAuthRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def get_user_by_email(self, email: str) -> UserAccount | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT id, nome, email, senha_hash, perfil, ativo
                FROM usuarios
                WHERE lower(email) = lower(%s)
                """,
                (email,),
            ).fetchone()
        if row is None:
            return None
        return UserAccount(
            id=row[0],
            nome=row[1],
            email=row[2],
            senha_hash=row[3],
            perfil=row[4],
            ativo=row[5],
        )

    def save_user(self, user: UserAccount) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO usuarios (id, nome, email, senha_hash, perfil, ativo)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    nome = EXCLUDED.nome,
                    email = EXCLUDED.email,
                    senha_hash = EXCLUDED.senha_hash,
                    perfil = EXCLUDED.perfil,
                    ativo = EXCLUDED.ativo,
                    updated_at = NOW()
                """,
                (
                    user.id,
                    user.nome,
                    user.email.lower(),
                    user.senha_hash,
                    user.perfil,
                    user.ativo,
                ),
            )
            connection.commit()

    def save_session(self, token_hash: str, session: AdminSession) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO admin_sessions (token_hash, user_id, expires_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (token_hash)
                DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    expires_at = EXCLUDED.expires_at,
                    created_at = NOW()
                """,
                (token_hash, session.user_id, session.expires_at),
            )
            connection.commit()

    def get_session(self, token_hash: str) -> AdminSession | None:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT u.id, u.perfil, u.ativo, s.expires_at
                FROM admin_sessions s
                JOIN usuarios u ON u.id = s.user_id
                WHERE s.token_hash = %s
                  AND s.expires_at > NOW()
                  AND u.ativo = TRUE
                """,
                (token_hash,),
            ).fetchone()
        if row is None:
            return None
        return AdminSession(
            user_id=row[0],
            perfil=row[1],
            ativo=row[2],
            expires_at=row[3],
        )

    def link_user_cliente(
        self,
        user_id: str,
        cliente_id: str,
        ativo: bool = True,
    ) -> None:
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO usuarios_clientes (usuario_id, cliente_id, ativo)
                VALUES (%s, %s, %s)
                ON CONFLICT (usuario_id, cliente_id)
                DO UPDATE SET ativo = EXCLUDED.ativo
                """,
                (user_id, cliente_id, ativo),
            )
            connection.commit()

    def grant_permission(
        self,
        user_id: str,
        recurso: str,
        acao: str,
        cliente_id: str | None = None,
        permitido: bool = True,
    ) -> str:
        permission_id = f"perm-{uuid4().hex}"
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO permissoes (
                    id,
                    usuario_id,
                    cliente_id,
                    recurso,
                    acao,
                    permitido
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (permission_id, user_id, cliente_id, recurso, acao, permitido),
            )
            connection.commit()
        return permission_id

    def has_cliente_access(self, user_id: str, cliente_id: str) -> bool:
        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM usuarios_clientes
                WHERE usuario_id = %s
                  AND cliente_id = %s
                  AND ativo = TRUE
                """,
                (user_id, cliente_id),
            ).fetchone()
        return row is not None

    def has_permission(
        self,
        user_id: str,
        recurso: str,
        acao: str,
        cliente_id: str | None = None,
    ) -> bool:
        if cliente_id is None:
            params = (user_id, recurso, acao)
            clause = "cliente_id IS NULL"
        else:
            params = (user_id, recurso, acao, cliente_id)
            clause = "(cliente_id = %s OR cliente_id IS NULL)"

        with psycopg.connect(self._database_url) as connection:
            row = connection.execute(
                f"""
                SELECT 1
                FROM permissoes
                WHERE usuario_id = %s
                  AND recurso = %s
                  AND acao = %s
                  AND permitido = TRUE
                  AND {clause}
                LIMIT 1
                """,
                params,
            ).fetchone()
        return row is not None

    def record_admin_access(
        self,
        user_id: str,
        recurso: str,
        acao: str,
        status: str,
        cliente_id: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> str:
        audit_id = f"audit-{uuid4().hex}"
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO auditoria_acessos (
                    id,
                    user_id,
                    cliente_id,
                    recurso,
                    acao,
                    status,
                    ip,
                    user_agent
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    audit_id,
                    user_id,
                    cliente_id,
                    recurso,
                    acao,
                    status,
                    ip,
                    user_agent,
                ),
            )
            connection.commit()
        return audit_id

    def list_admin_access_audits(
        self,
        limit: int = 50,
        offset: int = 0,
        user_id: str | None = None,
        cliente_id: str | None = None,
        recurso: str | None = None,
        acao: str | None = None,
        status: str | None = None,
    ) -> list[AdminAccessAudit]:
        clauses = []
        params: list[object] = []
        if user_id is not None:
            clauses.append("user_id = %s")
            params.append(user_id)
        if cliente_id is not None:
            clauses.append("cliente_id = %s")
            params.append(cliente_id)
        if recurso is not None:
            clauses.append("recurso = %s")
            params.append(recurso)
        if acao is not None:
            clauses.append("acao = %s")
            params.append(acao)
        if status is not None:
            clauses.append("status = %s")
            params.append(status)
        where = _where_clause(clauses)
        params.extend([limit, offset])
        with psycopg.connect(self._database_url) as connection:
            rows = connection.execute(
                f"""
                SELECT
                    user_id,
                    cliente_id,
                    recurso,
                    acao,
                    status,
                    ip,
                    user_agent,
                    criado_em
                FROM auditoria_acessos
                {where}
                ORDER BY criado_em DESC
                LIMIT %s OFFSET %s
                """,
                params,
            ).fetchall()
        return [
            AdminAccessAudit(
                user_id=row[0],
                cliente_id=row[1],
                recurso=row[2],
                acao=row[3],
                status=row[4],
                ip=row[5],
                user_agent=row[6],
                created_at=row[7],
            )
            for row in rows
        ]

    def ensure_default_admin(self, email: str, password: str) -> None:
        if self.get_user_by_email(email) is not None:
            return
        self.save_user(
            UserAccount(
                id=f"user-{uuid4().hex}",
                nome="Administrador",
                email=email.lower(),
                senha_hash=hash_password(password),
                perfil="admin",
                ativo=True,
            )
        )


def _where_clause(clauses: list[str]) -> str:
    if not clauses:
        return ""
    return "WHERE " + " AND ".join(clauses)
