# MoviProgy

Sistema Online de Midia Indoor com Sincronizacao Offline.

## Objetivo

Administrar propagandas remotamente e sincronizar imagens, videos e playlists para dispositivos de clientes.
O player deve baixar as midias, armazenar localmente e continuar exibindo conteudo mesmo sem internet.

## Estado atual

- Backend administrativo e contratos do player implementados em FastAPI.
- Frontend administrativo implementado com Vite, React e TypeScript.
- PostgreSQL, API, frontend e player integrados por Docker Compose.
- Testes automatizados de backend, frontend e player executados por CI.
- Player PWA offline-first implementado com IndexedDB, service worker e telemetria.
- Deploy publico depende da definicao de provedor, dominio, HTTPS e storage.

## Backend

Executar testes:

```powershell
python -m pytest
```

Executar API local:

```powershell
python -m uvicorn moviprogy_api.main:app --app-dir backend --reload
```

Executar com Docker:

```powershell
docker compose up --build -d
```

Painel integrado:

```text
http://127.0.0.1:8080
```

A porta `8080` publica o frontend e encaminha `/api` e `/health` para o backend.

Player:

```text
http://127.0.0.1:8091
```

A porta `8091` publica o player PWA e encaminha `/api` para o backend.

Smoke test integrado:

```powershell
.\scripts\smoke_stack.ps1 `
  -Email $env:MOVIPROGY_ADMIN_EMAIL `
  -Password $env:MOVIPROGY_ADMIN_PASSWORD
```

Pre-requisito:
- Docker Desktop precisa estar aberto e com daemon ativo.

Armazenamento local do projeto:
- `runtime/data`
- `runtime/media`
- `runtime/tmp`
- `runtime/postgres/data`
- `logs`

Persistencia atual:
- Sessoes demo do player no Docker: tabela `device_sessions` no PostgreSQL.
- Fallback sem banco: `runtime/data/device_registry.json`
- Tokens sao gravados apenas como SHA-256.
- Manifesto real usa `playlist_atual_id` do dispositivo quando ha dados no banco.
- Manifesto demo fica apenas como fallback local.

Observacao tecnica:
- O Compose usa bind mounts nessas pastas.
- Imagens, cache de build e camada interna do Docker ainda ficam no armazenamento global do Docker Desktop.
- Para nao usar o disco C nesses itens globais, e necessario mover o armazenamento do Docker Desktop nas configuracoes do Docker.

Simular player:

```powershell
.\scripts\simulate_player.ps1
```

Desenvolver o player:

```powershell
cd player
npm install
npm run dev
```

Testar e compilar:

```powershell
npm test
npm run build
```

Parar Docker:

```powershell
docker compose down
```

## Frontend

Executar painel local:

```powershell
cd frontend
npm install
npm run dev
```

- Painel: `http://127.0.0.1:5173`
- API local esperada: `http://127.0.0.1:8000`

Build:

```powershell
cd frontend
npm run build
```

Testes automatizados do frontend:

```powershell
cd frontend
npm test
```

Endpoints iniciais:

- `GET /health`
- `GET /health/ready`
- `GET /api/system/info`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `POST /api/player/ativar`
- `GET /api/player/playlist`
- `GET /api/player/atualizacao`
- `GET /api/player/midias/{midia_id}/download`
- `POST /api/player/status`
- `POST /api/player/logs`
- `POST /api/player/sincronizacao/confirmar`
- `POST /api/admin/clientes`
- `GET /api/admin/clientes`
- `GET /api/admin/clientes/{cliente_id}`
- `POST /api/admin/dispositivos`
- `GET /api/admin/dispositivos`
- `GET /api/admin/dispositivos/{dispositivo_id}`
- `GET /api/admin/dispositivos/{dispositivo_id}/eventos`
- `POST /api/admin/midias`
- `POST /api/admin/midias/upload`
- `GET /api/admin/midias`
- `GET /api/admin/midias/{midia_id}`
- `POST /api/admin/playlists`
- `GET /api/admin/playlists`
- `GET /api/admin/playlists/{playlist_id}`
- `POST /api/admin/playlists/{playlist_id}/midias`
- `GET /api/admin/auditoria/acessos`
- `POST /api/admin/auditoria/retencao/executar`
- `POST /api/admin/usuarios`
- `GET /api/admin/usuarios`
- `GET /api/admin/usuarios/{user_id}`
- `PATCH /api/admin/usuarios/{user_id}`
- `POST /api/admin/usuarios/{user_id}/clientes`
- `GET /api/admin/usuarios/{user_id}/clientes`
- `POST /api/admin/usuarios/{user_id}/permissoes`
- `GET /api/admin/usuarios/{user_id}/permissoes`

Limite:
- `/api/admin/*` exige `Authorization: Bearer <access_token>` de usuario com perfil `admin`.
- `ADMIN_API_TOKEN` permanece apenas como fallback local sem repository de auth.
- Listagens administrativas retornam `items`, `limit`, `offset` e `total`.
- Gestao de usuarios, vinculos e permissoes existe no backend.
- Google Drive possui implementacao inicial em `/api/integrations/google-drive`; OAuth real depende de credenciais Google Cloud.
- Configuracao local: `.\scripts\configure_google_oauth.ps1 -Simulated` para teste sem conta Google ou `-ClientId ... -ClientSecret ...` para OAuth real.

Banco local:
- PostgreSQL roda no container `moviprogy-db`.
- Dados ficam em `runtime/postgres/data`.
- Variaveis podem ser ajustadas em `.env`.
- Migration inicial: `backend/moviprogy_api/migrations/001_initial.sql`.
- Migration core: `backend/moviprogy_api/migrations/002_core_domain.sql`.
- Migration auth: `backend/moviprogy_api/migrations/003_auth.sql`.
- Migration eventos player: `backend/moviprogy_api/migrations/004_player_events.sql`.

Upload local:
- Arquivos ficam em `runtime/media`.
- Temporarios ficam em `runtime/tmp`.
- Limite padrao: 512 MB por arquivo.
- Variavel: `MOVIPROGY_MAX_UPLOAD_BYTES`.

Login admin local:

```powershell
$login = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/auth/login" `
  -ContentType "application/json" `
  -Body (@{
    email = $env:MOVIPROGY_ADMIN_EMAIL
    senha = $env:MOVIPROGY_ADMIN_PASSWORD
  } | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.access_token)" }
```

## Leitura obrigatoria antes de trabalhar

1. `AGENTS.md`
2. `PROJECT_RESUME.md`
3. `LESSONS_LEARNED.md`
4. `KNOWLEDGE_BASE.md`
5. `ARCHITECTURE_DECISIONS.md`

## Documentacao

- `docs/00-visao-geral/overview.md`
- `docs/01-requisitos/requisitos.md`
- `docs/02-arquitetura/arquitetura.md`
- `docs/03-banco-de-dados/modelo-dados.md`
- `docs/04-api/contratos-api.md`
- `docs/05-player/player-offline.md`
- `docs/06-testes/plano-testes.md`
- `docs/07-deploy/plano-deploy.md`
- `docs/08-governanca/backlog.md`
- `docs/08-governanca/decisoes.md`
- `docs/09-google-drive/integracao-google-drive.md`
- `docs/10-frontend/especificacao-frontend.md`
- `docs/11-seguranca/rbac-permissoes.md`
- `docs/12-storage/upload-download.md`
- `docs/13-player/especificacao-player.md`
- `docs/14-operacao/deploy-producao.md`
- `docs/14-operacao/backup-restore.md`
- `docs/14-operacao/observabilidade-logs.md`
- `docs/15-homologacao/checklist-homologacao.md`
- `docs/15-homologacao/matriz-testes.md`
- `docs/16-manuais/manual-admin.md`
- `docs/16-manuais/manual-operacional.md`

## Regra principal

Nenhuma implementacao deve iniciar sem consultar a memoria permanente do projeto e verificar decisoes, erros conhecidos e restricoes documentadas.
