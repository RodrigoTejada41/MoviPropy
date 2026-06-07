import hashlib
import errno
from pathlib import Path
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from moviprogy_api.domain.auth import AdminSession, UserAccount
from moviprogy_api.domain.core import Cliente, Dispositivo, Midia, Playlist
from moviprogy_api.main import create_app
from moviprogy_api.security import hash_token


ADMIN_TOKEN = "test-admin-session"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


class FakeCoreRepository:
    def __init__(self) -> None:
        self.clientes: dict[str, Cliente] = {}
        self.dispositivos: dict[str, Dispositivo] = {}
        self.midias: dict[str, Midia] = {}
        self.playlists: dict[str, Playlist] = {}
        self.playlist_midias: list[tuple[str, str, int, int | None]] = []

    def save_cliente(self, cliente: Cliente) -> None:
        self.clientes[cliente.id] = cliente

    def get_cliente(self, cliente_id: str) -> Cliente | None:
        return self.clientes.get(cliente_id)

    def list_clientes(
        self,
        limit: int = 50,
        offset: int = 0,
        ativo: bool | None = None,
    ) -> list[Cliente]:
        clientes = [
            cliente
            for cliente in self.clientes.values()
            if ativo is None or cliente.ativo is ativo
        ]
        return clientes[offset : offset + limit]

    def count_clientes(self, ativo: bool | None = None) -> int:
        return len(
            [
                cliente
                for cliente in self.clientes.values()
                if ativo is None or cliente.ativo is ativo
            ]
        )

    def save_dispositivo(self, dispositivo: Dispositivo) -> None:
        self.dispositivos[dispositivo.id] = dispositivo

    def get_dispositivo(self, dispositivo_id: str) -> Dispositivo | None:
        return self.dispositivos.get(dispositivo_id)

    def list_dispositivos(
        self,
        limit: int = 50,
        offset: int = 0,
        cliente_id: str | None = None,
        bloqueado: bool | None = None,
    ) -> list[Dispositivo]:
        dispositivos = [
            dispositivo
            for dispositivo in self.dispositivos.values()
            if (cliente_id is None or dispositivo.cliente_id == cliente_id)
            and (bloqueado is None or dispositivo.bloqueado is bloqueado)
        ]
        return dispositivos[offset : offset + limit]

    def count_dispositivos(
        self,
        cliente_id: str | None = None,
        bloqueado: bool | None = None,
    ) -> int:
        return len(
            [
                dispositivo
                for dispositivo in self.dispositivos.values()
                if (cliente_id is None or dispositivo.cliente_id == cliente_id)
                and (bloqueado is None or dispositivo.bloqueado is bloqueado)
            ]
        )

    def save_midia(self, midia: Midia) -> None:
        self.midias[midia.id] = midia

    def get_midia(self, midia_id: str) -> Midia | None:
        return self.midias.get(midia_id)

    def list_midias(
        self,
        limit: int = 50,
        offset: int = 0,
        cliente_id: str | None = None,
        ativo: bool | None = None,
    ) -> list[Midia]:
        midias = [
            midia
            for midia in self.midias.values()
            if (cliente_id is None or midia.cliente_id == cliente_id)
            and (ativo is None or midia.ativo is ativo)
        ]
        return midias[offset : offset + limit]

    def count_midias(
        self,
        cliente_id: str | None = None,
        ativo: bool | None = None,
    ) -> int:
        return len(
            [
                midia
                for midia in self.midias.values()
                if (cliente_id is None or midia.cliente_id == cliente_id)
                and (ativo is None or midia.ativo is ativo)
            ]
        )

    def save_playlist(self, playlist: Playlist) -> None:
        self.playlists[playlist.id] = playlist

    def get_playlist(self, playlist_id: str) -> Playlist | None:
        return self.playlists.get(playlist_id)

    def list_playlists(
        self,
        limit: int = 50,
        offset: int = 0,
        cliente_id: str | None = None,
        ativa: bool | None = None,
    ) -> list[Playlist]:
        playlists = [
            playlist
            for playlist in self.playlists.values()
            if (cliente_id is None or playlist.cliente_id == cliente_id)
            and (ativa is None or playlist.ativa is ativa)
        ]
        return playlists[offset : offset + limit]

    def count_playlists(
        self,
        cliente_id: str | None = None,
        ativa: bool | None = None,
    ) -> int:
        return len(
            [
                playlist
                for playlist in self.playlists.values()
                if (cliente_id is None or playlist.cliente_id == cliente_id)
                and (ativa is None or playlist.ativa is ativa)
            ]
        )

    def add_midia_to_playlist(
        self,
        playlist_id: str,
        midia_id: str,
        ordem: int,
        duracao_override: int | None = None,
    ) -> None:
        self.playlist_midias.append(
            (playlist_id, midia_id, ordem, duracao_override)
        )
        playlist = self.playlists[playlist_id]
        self.playlists[playlist_id] = playlist.model_copy(
            update={"versao": playlist.versao + 1}
        )

    def list_playlist_midias(self, playlist_id: str):
        return [
            {
                "playlist_id": item[0],
                "midia_id": item[1],
                "ordem": item[2],
                "duracao_override": item[3],
            }
            for item in self.playlist_midias
            if item[0] == playlist_id
        ]

    def remove_midia_from_playlist(self, playlist_id: str, midia_id: str) -> bool:
        before = len(self.playlist_midias)
        self.playlist_midias = [
            item
            for item in self.playlist_midias
            if not (item[0] == playlist_id and item[1] == midia_id)
        ]
        removed = len(self.playlist_midias) < before
        if removed:
            playlist = self.playlists[playlist_id]
            self.playlists[playlist_id] = playlist.model_copy(
                update={"versao": playlist.versao + 1}
            )
        return removed

    def list_sync_confirmations(
        self,
        limit=50,
        offset=0,
        cliente_id=None,
        dispositivo_id=None,
        status=None,
    ):
        items = []
        for device in self.dispositivos.values():
            if cliente_id is not None and device.cliente_id != cliente_id:
                continue
            if dispositivo_id is not None and device.id != dispositivo_id:
                continue
            items.append(
                {
                    "device_id": device.id,
                    "cliente_id": device.cliente_id,
                    "playlist_id": device.playlist_atual_id or "playlist-001",
                    "versao": 1,
                    "arquivos_baixados": [],
                    "status": "concluida",
                    "created_at": datetime.now(timezone.utc),
                }
            )
        if status is not None:
            items = [item for item in items if item["status"] == status]
        return items[offset : offset + limit]

    def count_sync_confirmations(
        self,
        cliente_id=None,
        dispositivo_id=None,
        status=None,
    ):
        return len(
            self.list_sync_confirmations(
                limit=10_000,
                cliente_id=cliente_id,
                dispositivo_id=dispositivo_id,
                status=status,
            )
        )

    def get_player_events_for_device(self, device_id: str) -> dict[str, list[dict]]:
        if device_id not in self.dispositivos:
            return {"status": [], "logs": [], "sync": []}
        return {
            "status": [{"status": "online", "versao_player": "0.1.0"}],
            "logs": [{"nivel": "info", "evento": "teste", "dados": {}}],
            "sync": [{"playlist_id": "playlist-001", "versao": 1, "status": "ok"}],
        }


class FakeAuthRepository:
    def __init__(
        self,
        perfil: str = "admin",
        user_id: str = "user-001",
        clientes: set[str] | None = None,
        permissions: set[tuple[str, str, str | None]] | None = None,
    ) -> None:
        self.user_id = user_id
        self.clientes = clientes or set()
        self.permissions = permissions or set()
        self.access_audits: list[dict] = []
        self.users: dict[str, UserAccount] = {}
        self.user_clientes: dict[tuple[str, str], bool] = {}
        self.user_permissions: list[dict] = []
        self.sessions = {
            hash_token(ADMIN_TOKEN): AdminSession(
                user_id=user_id,
                perfil=perfil,
                ativo=True,
            )
        }
        self.users[user_id] = UserAccount(
            id=user_id,
            nome="Admin Teste",
            email="admin@moviprogy.local",
            senha_hash="hash",
            perfil=perfil,
            ativo=True,
        )

    def get_session(self, token_hash: str) -> AdminSession | None:
        return self.sessions.get(token_hash)

    def get_user_by_id(self, user_id: str) -> UserAccount | None:
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> UserAccount | None:
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    def save_user(self, user: UserAccount) -> None:
        self.users[user.id] = user

    def list_users(
        self,
        limit: int = 50,
        offset: int = 0,
        ativo: bool | None = None,
        perfil: str | None = None,
    ) -> list[UserAccount]:
        users = [
            user
            for user in self.users.values()
            if (ativo is None or user.ativo is ativo)
            and (perfil is None or user.perfil == perfil)
        ]
        return sorted(users, key=lambda user: (user.nome, user.id))[
            offset : offset + limit
        ]

    def count_users(
        self,
        ativo: bool | None = None,
        perfil: str | None = None,
    ) -> int:
        return len(
            [
                user
                for user in self.users.values()
                if (ativo is None or user.ativo is ativo)
                and (perfil is None or user.perfil == perfil)
            ]
        )

    def has_cliente_access(self, user_id: str, cliente_id: str) -> bool:
        return (
            user_id == self.user_id
            and cliente_id in self.clientes
            or self.user_clientes.get((user_id, cliente_id)) is True
        )

    def link_user_cliente(
        self,
        user_id: str,
        cliente_id: str,
        ativo: bool = True,
    ) -> None:
        self.user_clientes[(user_id, cliente_id)] = ativo

    def list_user_clientes(self, user_id: str) -> list[dict]:
        return [
            {"user_id": uid, "cliente_id": cliente_id, "ativo": ativo}
            for (uid, cliente_id), ativo in self.user_clientes.items()
            if uid == user_id
        ]

    def grant_permission(
        self,
        user_id: str,
        recurso: str,
        acao: str,
        cliente_id: str | None = None,
        permitido: bool = True,
    ) -> str:
        permission_id = f"perm-{len(self.user_permissions) + 1}"
        self.user_permissions.append(
            {
                "id": permission_id,
                "user_id": user_id,
                "cliente_id": cliente_id,
                "recurso": recurso,
                "acao": acao,
                "permitido": permitido,
            }
        )
        return permission_id

    def list_user_permissions(self, user_id: str) -> list[dict]:
        return [
            permission
            for permission in self.user_permissions
            if permission["user_id"] == user_id
        ]

    def has_permission(
        self,
        user_id: str,
        recurso: str,
        acao: str,
        cliente_id: str | None = None,
    ) -> bool:
        if user_id != self.user_id:
            return False
        return (recurso, acao, cliente_id) in self.permissions or (
            recurso,
            acao,
            None,
        ) in self.permissions

    def record_admin_access(
        self,
        user_id: str,
        recurso: str,
        acao: str,
        status: str,
        cliente_id: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        self.access_audits.append(
            {
                "user_id": user_id,
                "recurso": recurso,
                "acao": acao,
                "status": status,
                "cliente_id": cliente_id,
                "ip": ip,
                "user_agent": user_agent,
            }
        )

    def list_admin_access_audits(
        self,
        limit: int = 50,
        offset: int = 0,
        user_id: str | None = None,
        cliente_id: str | None = None,
        recurso: str | None = None,
        acao: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        audits = [
            audit
            for audit in self.access_audits
            if (user_id is None or audit["user_id"] == user_id)
            and (cliente_id is None or audit["cliente_id"] == cliente_id)
            and (recurso is None or audit["recurso"] == recurso)
            and (acao is None or audit["acao"] == acao)
            and (status is None or audit["status"] == status)
        ]
        return audits[offset : offset + limit]

    def count_admin_access_audits(
        self,
        user_id: str | None = None,
        cliente_id: str | None = None,
        recurso: str | None = None,
        acao: str | None = None,
        status: str | None = None,
    ) -> int:
        return len(
            [
                audit
                for audit in self.access_audits
                if (user_id is None or audit["user_id"] == user_id)
                and (cliente_id is None or audit["cliente_id"] == cliente_id)
                and (recurso is None or audit["recurso"] == recurso)
                and (acao is None or audit["acao"] == acao)
                and (status is None or audit["status"] == status)
            ]
        )

    def delete_admin_access_audits_older_than(self, cutoff) -> int:
        before = len(self.access_audits)
        self.access_audits = [
            audit
            for audit in self.access_audits
            if audit.get("created_at") is None or audit["created_at"] >= cutoff
        ]
        return before - len(self.access_audits)


def _create_test_app(
    perfil: str = "admin",
    clientes: set[str] | None = None,
    permissions: set[tuple[str, str, str | None]] | None = None,
):
    app = create_app()
    app.state.core_repository = FakeCoreRepository()
    app.state.auth_repository = FakeAuthRepository(
        perfil=perfil,
        clientes=clientes,
        permissions=permissions,
    )
    return app


def test_admin_rejects_missing_token():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/clientes",
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "token ausente"}


def test_admin_rejects_invalid_token():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/clientes",
        headers={"Authorization": "Bearer invalid"},
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "token invalido"}


def test_admin_rejects_non_admin_user():
    app = _create_test_app(perfil="operador")
    client = TestClient(app)

    response = client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "permissao insuficiente"}


def test_admin_allows_scoped_user_with_cliente_and_permission():
    app = _create_test_app(
        perfil="admin_cliente",
        clientes={"cliente-001"},
        permissions={("midias", "criar", "cliente-001")},
    )
    client = TestClient(app)
    app.state.core_repository.save_cliente(
        Cliente(id="cliente-001", nome="Cliente Um")
    )

    response = client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == "midia-001"
    assert app.state.auth_repository.access_audits[-1] == {
        "user_id": "user-001",
        "recurso": "midias",
        "acao": "criar",
        "status": "permitido",
        "cliente_id": "cliente-001",
        "ip": "testclient",
        "user_agent": "testclient",
    }


def test_admin_blocks_scoped_user_for_unlinked_cliente():
    app = _create_test_app(
        perfil="admin_cliente",
        clientes={"cliente-001"},
        permissions={("midias", "criar", "cliente-002")},
    )
    client = TestClient(app)
    app.state.core_repository.save_cliente(
        Cliente(id="cliente-002", nome="Cliente Dois")
    )

    response = client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-002",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "permissao insuficiente"}
    assert app.state.auth_repository.access_audits[-1]["status"] == "negado"
    assert app.state.auth_repository.access_audits[-1]["cliente_id"] == "cliente-002"


def test_admin_blocks_scoped_user_without_action_permission():
    app = _create_test_app(
        perfil="admin_cliente",
        clientes={"cliente-001"},
        permissions={("midias", "ler", "cliente-001")},
    )
    client = TestClient(app)
    app.state.core_repository.save_cliente(
        Cliente(id="cliente-001", nome="Cliente Um")
    )

    response = client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "permissao insuficiente"}
    assert app.state.auth_repository.access_audits[-1]["status"] == "negado"
    assert app.state.auth_repository.access_audits[-1]["acao"] == "criar"


def test_admin_creates_and_lists_users_without_password_hash():
    app = _create_test_app()
    client = TestClient(app)

    create_response = client.post(
        "/api/admin/usuarios",
        headers=ADMIN_HEADERS,
        json={
            "id": "user-002",
            "nome": "Operador Um",
            "email": "operador@moviprogy.local",
            "senha": "senha-segura",
            "perfil": "operador",
            "ativo": True,
        },
    )
    list_response = client.get(
        "/api/admin/usuarios?perfil=operador",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json() == {
        "id": "user-002",
        "nome": "Operador Um",
        "email": "operador@moviprogy.local",
        "perfil": "operador",
        "ativo": True,
    }
    assert "senha_hash" not in create_response.text
    assert "senha-segura" not in create_response.text
    payload = list_response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "user-002"


def test_admin_rejects_duplicate_user_email():
    app = _create_test_app()
    client = TestClient(app)
    payload = {
        "id": "user-002",
        "nome": "Operador Um",
        "email": "operador@moviprogy.local",
        "senha": "senha-segura",
        "perfil": "operador",
    }
    client.post("/api/admin/usuarios", headers=ADMIN_HEADERS, json=payload)

    response = client.post(
        "/api/admin/usuarios",
        headers=ADMIN_HEADERS,
        json={**payload, "id": "user-003"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "email ja cadastrado"}


def test_admin_links_user_to_cliente_and_grants_permission():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/usuarios",
        headers=ADMIN_HEADERS,
        json={
            "id": "user-002",
            "nome": "Operador Um",
            "email": "operador@moviprogy.local",
            "senha": "senha-segura",
            "perfil": "operador",
        },
    )

    link_response = client.post(
        "/api/admin/usuarios/user-002/clientes",
        headers=ADMIN_HEADERS,
        json={"cliente_id": "cliente-001", "ativo": True},
    )
    permission_response = client.post(
        "/api/admin/usuarios/user-002/permissoes",
        headers=ADMIN_HEADERS,
        json={
            "recurso": "midias",
            "acao": "upload",
            "cliente_id": "cliente-001",
            "permitido": True,
        },
    )

    assert link_response.status_code == 201
    assert link_response.json() == {
        "user_id": "user-002",
        "cliente_id": "cliente-001",
        "ativo": True,
    }
    assert permission_response.status_code == 201
    assert permission_response.json()["recurso"] == "midias"
    assert permission_response.json()["acao"] == "upload"
    assert permission_response.json()["cliente_id"] == "cliente-001"


def test_admin_rejects_user_link_for_missing_cliente():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/usuarios",
        headers=ADMIN_HEADERS,
        json={
            "id": "user-002",
            "nome": "Operador Um",
            "email": "operador@moviprogy.local",
            "senha": "senha-segura",
            "perfil": "operador",
        },
    )

    response = client.post(
        "/api/admin/usuarios/user-002/clientes",
        headers=ADMIN_HEADERS,
        json={"cliente_id": "cliente-inexistente"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "cliente_id invalido"}


def test_admin_blocks_user_management_without_permission():
    app = _create_test_app(perfil="operador")
    client = TestClient(app)

    response = client.post(
        "/api/admin/usuarios",
        headers=ADMIN_HEADERS,
        json={
            "id": "user-002",
            "nome": "Operador Um",
            "email": "operador@moviprogy.local",
            "senha": "senha-segura",
            "perfil": "operador",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "permissao insuficiente"}


def test_admin_lists_access_audits_with_filters():
    app = _create_test_app()
    client = TestClient(app)
    app.state.auth_repository.record_admin_access(
        user_id="user-001",
        recurso="clientes",
        acao="ler",
        status="permitido",
        cliente_id="cliente-001",
        ip="127.0.0.1",
        user_agent="pytest",
    )
    app.state.auth_repository.record_admin_access(
        user_id="user-002",
        recurso="midias",
        acao="criar",
        status="negado",
        cliente_id="cliente-002",
        ip="127.0.0.1",
        user_agent="pytest",
    )

    response = client.get(
        "/api/admin/auditoria/acessos?cliente_id=cliente-002&status=negado",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 50
    assert payload["offset"] == 0
    assert payload["total"] == 1
    assert payload["items"] == [
        {
            "user_id": "user-002",
            "recurso": "midias",
            "acao": "criar",
            "status": "negado",
            "cliente_id": "cliente-002",
            "ip": "127.0.0.1",
            "user_agent": "pytest",
            "created_at": None,
        }
    ]


def test_admin_requires_cliente_for_scoped_audit_list():
    app = _create_test_app(
        perfil="admin_cliente",
        clientes={"cliente-001"},
        permissions={("auditoria", "ler", "cliente-001")},
    )
    client = TestClient(app)

    response = client.get(
        "/api/admin/auditoria/acessos",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "cliente_id obrigatorio"}


def test_admin_allows_scoped_audit_list_for_linked_cliente():
    app = _create_test_app(
        perfil="admin_cliente",
        clientes={"cliente-001"},
        permissions={("auditoria", "ler", "cliente-001")},
    )
    client = TestClient(app)
    app.state.auth_repository.record_admin_access(
        user_id="user-001",
        recurso="midias",
        acao="criar",
        status="permitido",
        cliente_id="cliente-001",
    )

    response = client.get(
        "/api/admin/auditoria/acessos?cliente_id=cliente-001",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert {item["cliente_id"] for item in payload["items"]} == {"cliente-001"}


def test_admin_executes_audit_retention_policy():
    app = _create_test_app()
    client = TestClient(app)
    old_date = datetime.now(timezone.utc) - timedelta(days=200)
    recent_date = datetime.now(timezone.utc) - timedelta(days=10)
    app.state.auth_repository.access_audits.append(
        {
            "user_id": "user-001",
            "recurso": "clientes",
            "acao": "ler",
            "status": "permitido",
            "cliente_id": None,
            "ip": "127.0.0.1",
            "user_agent": "pytest",
            "created_at": old_date,
        }
    )
    app.state.auth_repository.access_audits.append(
        {
            "user_id": "user-001",
            "recurso": "clientes",
            "acao": "ler",
            "status": "permitido",
            "cliente_id": None,
            "ip": "127.0.0.1",
            "user_agent": "pytest",
            "created_at": recent_date,
        }
    )

    response = client.post(
        "/api/admin/auditoria/retencao/executar?dias=180",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["deleted_count"] == 1
    assert len(app.state.auth_repository.access_audits) == 2
    assert old_date not in [
        audit.get("created_at") for audit in app.state.auth_repository.access_audits
    ]


def test_admin_creates_and_gets_cliente():
    app = _create_test_app()
    client = TestClient(app)

    create_response = client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um", "documento": "123"},
    )
    get_response = client.get(
        "/api/admin/clientes/cliente-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json() == {
        "id": "cliente-001",
        "nome": "Cliente Um",
        "documento": "123",
        "ativo": True,
    }
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == "Cliente Um"


def test_admin_lists_clientes():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-002", "nome": "Cliente Dois"},
    )

    response = client.get("/api/admin/clientes", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 50
    assert payload["offset"] == 0
    assert payload["total"] == 2
    assert [cliente["id"] for cliente in payload["items"]] == [
        "cliente-001",
        "cliente-002",
    ]


def test_admin_lists_clientes_with_pagination_and_active_filter():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id, ativo in (
        ("cliente-001", True),
        ("cliente-002", False),
        ("cliente-003", True),
    ):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id, "ativo": ativo},
        )

    response = client.get(
        "/api/admin/clientes?ativo=true&limit=1&offset=1",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 1
    assert payload["offset"] == 1
    assert payload["total"] == 2
    assert [cliente["id"] for cliente in payload["items"]] == ["cliente-003"]


def test_admin_rejects_list_limit_above_maximum():
    app = _create_test_app()
    client = TestClient(app)

    response = client.get(
        "/api/admin/clientes?limit=201",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 422


def test_admin_returns_404_for_missing_cliente():
    app = _create_test_app()
    client = TestClient(app)

    response = client.get(
        "/api/admin/clientes/inexistente",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "cliente nao encontrado"}


def test_admin_creates_and_gets_dispositivo():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    create_response = client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )
    get_response = client.get(
        "/api/admin/dispositivos/device-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json()["codigo_ativacao"] == "CODE-001"
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == "TV Entrada"


def test_admin_generates_dispositivo_id_and_activation_code():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    first_response = client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={"cliente_id": "cliente-001", "nome": "JECA TV"},
    )
    second_response = client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={"cliente_id": "cliente-001", "nome": "JECA TV"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["id"] == "JECA_TV01"
    assert second_response.json()["id"] == "JECA_TV02"
    assert first_response.json()["codigo_ativacao"].startswith("MOVI-")
    assert second_response.json()["codigo_ativacao"].startswith("MOVI-")
    assert first_response.json()["codigo_ativacao"] != second_response.json()["codigo_ativacao"]


def test_admin_lists_dispositivos():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )

    response = client.get("/api/admin/dispositivos", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "device-001"


def test_admin_lists_dispositivos_with_cliente_and_blocked_filters():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id in ("cliente-001", "cliente-002"):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id},
        )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV 1",
            "codigo_ativacao": "CODE-001",
            "bloqueado": False,
        },
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-002",
            "cliente_id": "cliente-001",
            "nome": "TV 2",
            "codigo_ativacao": "CODE-002",
            "bloqueado": True,
        },
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-003",
            "cliente_id": "cliente-002",
            "nome": "TV 3",
            "codigo_ativacao": "CODE-003",
            "bloqueado": True,
        },
    )

    response = client.get(
        "/api/admin/dispositivos?cliente_id=cliente-001&bloqueado=true",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [dispositivo["id"] for dispositivo in payload["items"]] == ["device-002"]


def test_admin_gets_dispositivo_events():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )

    response = client.get(
        "/api/admin/dispositivos/device-001/eventos",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"][0]["status"] == "online"


def test_admin_rejects_dispositivo_for_missing_cliente():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-inexistente",
            "nome": "TV Entrada",
            "codigo_ativacao": "CODE-001",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "cliente_id invalido"}


def test_admin_creates_and_gets_midia():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    create_response = client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
            "duracao_segundos": 30,
        },
    )
    get_response = client.get(
        "/api/admin/midias/midia-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json()["nome"] == "Video Entrada"
    assert get_response.status_code == 200
    assert get_response.json()["sha256"] == "a" * 64


def test_admin_lists_midias():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )

    response = client.get("/api/admin/midias", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "midia-001"


def test_admin_lists_midias_with_cliente_and_active_filters():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id in ("cliente-001", "cliente-002"):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id},
        )
    for midia_id, cliente_id, ativo in (
        ("midia-001", "cliente-001", True),
        ("midia-002", "cliente-001", False),
        ("midia-003", "cliente-002", False),
    ):
        client.post(
            "/api/admin/midias",
            headers=ADMIN_HEADERS,
            json={
                "id": midia_id,
                "cliente_id": cliente_id,
                "nome": midia_id,
                "tipo": "video",
                "caminho": f"media/{midia_id}.mp4",
                "tamanho": 1024,
                "sha256": "a" * 64,
                "ativo": ativo,
            },
        )

    response = client.get(
        "/api/admin/midias?cliente_id=cliente-001&ativo=false",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [midia["id"] for midia in payload["items"]] == ["midia-002"]


def test_admin_rejects_midia_for_missing_cliente():
    app = _create_test_app()
    client = TestClient(app)

    response = client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-inexistente",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "cliente_id invalido"}


def test_admin_uploads_valid_video_midia(tmp_path):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    content = b"video-content"

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={
            "cliente_id": "cliente-001",
            "tipo": "video",
            "duracao_segundos": "30",
        },
        files={"arquivo": ("entrada.mp4", content, "video/mp4")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["cliente_id"] == "cliente-001"
    assert payload["nome"] == "entrada.mp4"
    assert payload["tipo"] == "video"
    assert payload["tamanho"] == len(content)
    assert payload["sha256"] == hashlib.sha256(content).hexdigest()
    saved = app.state.media_dir / payload["caminho"]
    assert saved.read_bytes() == content
    assert app.state.core_repository.get_midia(payload["id"]) == Midia(**payload)


def test_admin_upload_rejects_invalid_file_type(tmp_path):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={"cliente_id": "cliente-001", "tipo": "video"},
        files={"arquivo": ("entrada.exe", b"invalid", "application/octet-stream")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "arquivo invalido"}
    assert app.state.core_repository.midias == {}


def test_admin_upload_rejects_file_over_size_limit(tmp_path):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    app.state.max_upload_bytes = 4
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={"cliente_id": "cliente-001", "tipo": "video"},
        files={"arquivo": ("entrada.mp4", b"12345", "video/mp4")},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "arquivo excede tamanho maximo"}
    assert app.state.core_repository.midias == {}
    assert not any((tmp_path / "media").rglob("*"))


def test_admin_upload_handles_cross_device_tmp_and_media_dirs(
    tmp_path,
    monkeypatch,
):
    app = _create_test_app()
    app.state.media_dir = tmp_path / "media"
    app.state.tmp_dir = tmp_path / "tmp"
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    def fail_replace(self, target):
        raise OSError(errno.EXDEV, "Invalid cross-device link")

    monkeypatch.setattr(Path, "replace", fail_replace)

    response = client.post(
        "/api/admin/midias/upload",
        headers=ADMIN_HEADERS,
        data={"cliente_id": "cliente-001", "tipo": "video"},
        files={"arquivo": ("entrada.mp4", b"video", "video/mp4")},
    )

    assert response.status_code == 201
    saved = app.state.media_dir / response.json()["caminho"]
    assert saved.read_bytes() == b"video"


def test_admin_creates_and_gets_playlist():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )

    create_response = client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={
            "id": "playlist-001",
            "cliente_id": "cliente-001",
            "nome": "Playlist Principal",
            "versao": 1,
            "ativa": True,
        },
    )
    get_response = client.get(
        "/api/admin/playlists/playlist-001",
        headers=ADMIN_HEADERS,
    )

    assert create_response.status_code == 201
    assert create_response.json()["ativa"] is True
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == "Playlist Principal"


def test_admin_lists_playlists():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={
            "id": "playlist-001",
            "cliente_id": "cliente-001",
            "nome": "Playlist Principal",
        },
    )

    response = client.get("/api/admin/playlists", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == "playlist-001"


def test_admin_lists_playlists_with_cliente_and_active_filters():
    app = _create_test_app()
    client = TestClient(app)
    for cliente_id in ("cliente-001", "cliente-002"):
        client.post(
            "/api/admin/clientes",
            headers=ADMIN_HEADERS,
            json={"id": cliente_id, "nome": cliente_id},
        )
    for playlist_id, cliente_id, ativa in (
        ("playlist-001", "cliente-001", True),
        ("playlist-002", "cliente-001", False),
        ("playlist-003", "cliente-002", False),
    ):
        client.post(
            "/api/admin/playlists",
            headers=ADMIN_HEADERS,
            json={
                "id": playlist_id,
                "cliente_id": cliente_id,
                "nome": playlist_id,
                "ativa": ativa,
            },
        )

    response = client.get(
        "/api/admin/playlists?cliente_id=cliente-001&ativa=false",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [playlist["id"] for playlist in payload["items"]] == ["playlist-002"]


def test_admin_links_midia_to_playlist():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )
    client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={
            "id": "playlist-001",
            "cliente_id": "cliente-001",
            "nome": "Playlist Principal",
        },
    )

    response = client.post(
        "/api/admin/playlists/playlist-001/midias",
        headers=ADMIN_HEADERS,
        json={"midia_id": "midia-001", "ordem": 1, "duracao_override": 20},
    )

    assert response.status_code == 201
    assert response.json() == {
        "playlist_id": "playlist-001",
        "midia_id": "midia-001",
        "ordem": 1,
        "duracao_override": 20,
    }


def test_admin_rejects_link_when_midia_belongs_to_other_cliente():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente Um"},
    )
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-002", "nome": "Cliente Dois"},
    )
    client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Video Entrada",
            "tipo": "video",
            "caminho": "media/video.mp4",
            "tamanho": 1024,
            "sha256": "a" * 64,
        },
    )
    client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={
            "id": "playlist-001",
            "cliente_id": "cliente-002",
            "nome": "Playlist Cliente Dois",
        },
    )

    response = client.post(
        "/api/admin/playlists/playlist-001/midias",
        headers=ADMIN_HEADERS,
        json={"midia_id": "midia-001", "ordem": 1},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "midia de outro cliente"}


def test_admin_updates_cliente():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Original", "ativo": True},
    )

    response = client.patch(
        "/api/admin/clientes/cliente-001",
        headers=ADMIN_HEADERS,
        json={"nome": "Atualizado", "ativo": False},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Atualizado"
    assert response.json()["ativo"] is False


def test_admin_updates_and_blocks_dispositivo():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente"},
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV",
            "codigo_ativacao": "CODE-001",
        },
    )

    response = client.patch(
        "/api/admin/dispositivos/device-001",
        headers=ADMIN_HEADERS,
        json={"nome": "TV Recepcao", "bloqueado": True},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "TV Recepcao"
    assert response.json()["bloqueado"] is True


def test_admin_updates_midia_status():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente"},
    )
    client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Imagem",
            "tipo": "imagem",
            "caminho": "imagem.png",
            "tamanho": 10,
            "sha256": "a" * 64,
        },
    )

    response = client.patch(
        "/api/admin/midias/midia-001",
        headers=ADMIN_HEADERS,
        json={"nome": "Imagem Atualizada", "ativo": False},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Imagem Atualizada"
    assert response.json()["ativo"] is False


def test_admin_updates_playlist_lists_and_removes_media():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente"},
    )
    client.post(
        "/api/admin/midias",
        headers=ADMIN_HEADERS,
        json={
            "id": "midia-001",
            "cliente_id": "cliente-001",
            "nome": "Imagem",
            "tipo": "imagem",
            "caminho": "imagem.png",
            "tamanho": 10,
            "sha256": "a" * 64,
        },
    )
    client.post(
        "/api/admin/playlists",
        headers=ADMIN_HEADERS,
        json={"id": "playlist-001", "cliente_id": "cliente-001", "nome": "Principal"},
    )
    client.post(
        "/api/admin/playlists/playlist-001/midias",
        headers=ADMIN_HEADERS,
        json={"midia_id": "midia-001", "ordem": 1},
    )

    update = client.patch(
        "/api/admin/playlists/playlist-001",
        headers=ADMIN_HEADERS,
        json={"nome": "Principal Atualizada", "ativa": True},
    )
    items = client.get(
        "/api/admin/playlists/playlist-001/midias",
        headers=ADMIN_HEADERS,
    )
    removal = client.delete(
        "/api/admin/playlists/playlist-001/midias/midia-001",
        headers=ADMIN_HEADERS,
    )

    assert update.status_code == 200
    assert update.json()["ativa"] is True
    assert update.json()["versao"] == 3
    assert items.status_code == 200
    assert items.json()[0]["midia_id"] == "midia-001"
    assert removal.status_code == 204


def test_admin_lists_sync_confirmations():
    app = _create_test_app()
    client = TestClient(app)
    client.post(
        "/api/admin/clientes",
        headers=ADMIN_HEADERS,
        json={"id": "cliente-001", "nome": "Cliente"},
    )
    client.post(
        "/api/admin/dispositivos",
        headers=ADMIN_HEADERS,
        json={
            "id": "device-001",
            "cliente_id": "cliente-001",
            "nome": "TV",
            "codigo_ativacao": "CODE-001",
        },
    )

    response = client.get(
        "/api/admin/sincronizacoes?cliente_id=cliente-001",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["device_id"] == "device-001"


def test_admin_returns_safe_operational_configuration():
    app = _create_test_app()
    app.state.max_upload_bytes = 1024
    client = TestClient(app)

    response = client.get("/api/admin/configuracoes", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    assert response.json() == {
        "storage_provider": "local",
        "max_upload_bytes": 1024,
        "offline_first": True,
    }
