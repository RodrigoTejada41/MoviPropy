# MoviProgy

Sistema Online de Midia Indoor com Sincronizacao Offline.

## Objetivo

Administrar propagandas remotamente e sincronizar imagens, videos e playlists para dispositivos de clientes.
O player deve baixar as midias, armazenar localmente e continuar exibindo conteudo mesmo sem internet.

## Estado atual

- Projeto em fase de documentacao inicial.
- Backend minimo criado com FastAPI.
- Testes iniciais criados com pytest.
- Stack frontend ainda nao aprovada.
- Documentacao base criada.

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

Parar Docker:

```powershell
docker compose down
```

Endpoints iniciais:

- `GET /health`
- `GET /health/ready`
- `GET /api/system/info`
- `POST /api/auth/login`
- `POST /api/player/ativar`
- `GET /api/player/playlist`
- `GET /api/player/midias/{midia_id}/download`
- `POST /api/admin/clientes`
- `GET /api/admin/clientes/{cliente_id}`
- `POST /api/admin/dispositivos`
- `GET /api/admin/dispositivos/{dispositivo_id}`
- `POST /api/admin/midias`
- `POST /api/admin/midias/upload`
- `GET /api/admin/midias/{midia_id}`
- `POST /api/admin/playlists`
- `GET /api/admin/playlists/{playlist_id}`
- `POST /api/admin/playlists/{playlist_id}/midias`

Limite:
- `/api/admin/*` exige `Authorization: Bearer <access_token>` de usuario com perfil `admin`.
- `ADMIN_API_TOKEN` permanece apenas como fallback local sem repository de auth.
- RBAC granular por cliente/acao ainda esta pendente.

Banco local:
- PostgreSQL roda no container `moviprogy-db`.
- Dados ficam em `runtime/postgres/data`.
- Variaveis podem ser ajustadas em `.env`.
- Migration inicial: `backend/moviprogy_api/migrations/001_initial.sql`.
- Migration core: `backend/moviprogy_api/migrations/002_core_domain.sql`.
- Migration auth: `backend/moviprogy_api/migrations/003_auth.sql`.

Upload local:
- Arquivos ficam em `runtime/media`.
- Temporarios ficam em `runtime/tmp`.
- Limite padrao: 512 MB por arquivo.
- Variavel: `MOVIPROGY_MAX_UPLOAD_BYTES`.

Login admin local padrao do Compose:

```powershell
$login = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/auth/login" `
  -ContentType "application/json" `
  -Body '{"email":"admin@moviprogy.local","senha":"moviprogy_admin_dev_password"}'
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
