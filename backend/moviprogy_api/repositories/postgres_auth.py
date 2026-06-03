from datetime import datetime, timezone
from uuid import uuid4

import psycopg

from moviprogy_api.domain.auth import AdminSession, UserAccount
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
