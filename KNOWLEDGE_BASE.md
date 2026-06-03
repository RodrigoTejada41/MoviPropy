# KNOWLEDGE_BASE.md

## Objetivo

Centralizar conhecimento tecnico, restricoes, padroes obrigatorios e decisoes relevantes do projeto.

## Contexto do sistema

Sistema de midia indoor para administrar campanhas online e reproduzir conteudo em dispositivos remotos.

## Restricoes obrigatorias

- Painel administrativo deve ser online.
- Player deve funcionar offline.
- Player deve manter ultima playlist valida.
- Midia antiga nao pode ser removida antes da nova ser baixada e validada.
- Sistema deve suportar varios clientes.
- Dados devem ser isolados por cliente.
- Upload deve validar extensao, tamanho e tipo.
- HTTPS e obrigatorio em ambiente publicado.

## Padroes obrigatorios

- Documentacao antes de implementacao.
- Teste antes de codigo para regra de negocio.
- Queries parametrizadas.
- Senhas com hash.
- Tokens unicos por dispositivo.
- Controle de permissao por perfil.
- Logs de sincronizacao.
- Health checks no backend.
- Backups antes de migracoes.
- Manifesto so pode ser ativado quando todos os arquivos passarem por validacao de tamanho e hash.

## Conhecimento tecnico atual

- Backend definido: Python 3.12+ com FastAPI.
- Testes definidos: pytest com FastAPI TestClient.
- Documentacao funcional, tecnica, operacional e de homologacao foi fechada como baseline antes de continuar backend/frontend.
- Banco definido para ambiente Docker local: PostgreSQL.
- Contratos iniciais do player persistem sessoes no PostgreSQL quando `DATABASE_URL` existe.
- Contratos do player consultam dispositivo e manifesto real no PostgreSQL quando `core_repository` existe.
- Login administrativo persiste sessoes no PostgreSQL quando `DATABASE_URL` existe.
- Docker Compose executa o backend em `moviprogy-api`.
- Docker Compose executa PostgreSQL em `moviprogy-db`.
- Dados de runtime do container devem usar bind mounts em `runtime/` e `logs/` dentro do projeto.
- Storage local inicial definido em `MOVIPROGY_MEDIA_DIR`.
- Google Drive esta documentado como opcao planejada de storage externo controlado pelo backend.
- Player ainda nao definido.
- Deploy ainda nao definido alem do container local.

## Documentacao baseline

Arquivos obrigatorios para continuidade:
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

Regra:
- Antes de implementar backend, consultar docs de API, banco, storage, seguranca, testes e operacao.
- Antes de implementar frontend, consultar `docs/10-frontend/especificacao-frontend.md`.
- Antes de implementar player, consultar `docs/13-player/especificacao-player.md`.

## Banco local

- Engine: PostgreSQL.
- Container: `moviprogy-db`.
- Dados: `runtime/postgres/data`.
- Health da API: `GET /health/ready`.
- Driver Python: psycopg 3.

Limite:
- Repository de sessoes usa PostgreSQL.
- Entidades `clientes`, `dispositivos`, `midias`, `playlists` e `playlist_midias` possuem tabelas.
- Repository core persiste entidades iniciais do dominio.
- Rotas administrativas existem para clientes, dispositivos, midias e playlists.
- Vinculo de midia em playlist existe via rota administrativa.
- Tabelas `usuarios` e `admin_sessions` implementam login administrativo inicial.

## Integracao Google Drive planejada

- Documento principal: `docs/09-google-drive/integracao-google-drive.md`.
- Player nao deve fazer streaming direto do Google Drive.
- Player nao deve receber credenciais Google.
- Backend deve gerar link controlado ou temporario de download.
- Player deve baixar a midia, validar tamanho/hash e reproduzir localmente.
- OAuth 2.0 deve ser usado para conexao com Google Drive.
- Refresh token deve ser protegido; nao pode ficar em texto puro.
- Arquivos e pastas devem ser isolados por cliente.
- RBAC real e obrigatorio antes de expor a integracao em producao.

## Riscos conhecidos

- Sincronizacao offline e ponto critico.
- Falha durante download nao pode quebrar playlist funcional.
- Isolamento multi-cliente deve ser validado desde o inicio.
- Storage local pode virar gargalo se houver muitos videos.
- Logs de runtime devem ficar fora do versionamento.

## Stack aprovada operacionalmente

- Backend/API: Python 3.12+ e FastAPI.
- Testes backend: pytest.
- Servidor ASGI: uvicorn.

## Contratos atuais do player

- `POST /api/player/ativar`: ativa dispositivo por codigo e retorna token.
- `GET /api/player/playlist`: retorna manifesto ativo mediante token Bearer.

Implementacao atual:
- Ativacao real usa `dispositivos.codigo_ativacao`.
- Dispositivo bloqueado nao ativa pelo fluxo real.
- Manifesto real usa `dispositivos.playlist_atual_id`.
- Playlist precisa estar ativa.
- Arquivos do manifesto sao gerados por `playlist_midias` ordenado por `ordem`.
- Somente midias ativas entram no manifesto.

Limite:
- Manifesto demo ainda existe como fallback sem playlist real.
- Sessoes do player usam PostgreSQL quando `DATABASE_URL` existe.
- JSON e apenas fallback para execucao sem banco.
- Upload fisico local existe em `POST /api/admin/midias/upload`.
- Download controlado implementado em `GET /api/player/midias/{midia_id}/download`.
- Download so libera midia ativa vinculada a playlist atual ativa do dispositivo.

Persistencia atual:
- Tabela: `device_sessions`.
- Tabelas core: `clientes`, `dispositivos`, `midias`, `playlists`, `playlist_midias`.
- Variavel: `DATABASE_URL`.
- Escopo: sessoes de dispositivo.
- Tokens sao armazenados somente como SHA-256.
- Manifestos demo ainda ficam em memoria.
- Manifesto real e retornado quando dispositivo possui playlist atual ativa no banco.
- Arquivos locais sao servidos a partir de `MOVIPROGY_MEDIA_DIR`.
- Caminhos de midia sao resolvidos dentro do diretorio base para bloquear path traversal.
- Upload local salva arquivos em `clientes/{cliente_id}/midias/{midia_id}/original.ext`.
- Limite padrao de upload: `MOVIPROGY_MAX_UPLOAD_BYTES`, default 512 MB.

## Rotas administrativas atuais

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

Seguranca:
- Exigem `Authorization: Bearer <access_token>` retornado por `POST /api/auth/login`.
- Usuario precisa ter perfil `admin`.
- `ADMIN_API_TOKEN` existe apenas como fallback local quando `auth_repository` nao esta disponivel.

Limite:
- RBAC atual ainda nao possui permissao granular por cliente/acao.
- Sessao admin usa hash SHA-256 do token no banco.
- Senha usa PBKDF2-HMAC-SHA256 com salt individual.

Regras de negocio atuais:
- Midia so pode ser criada para cliente existente.
- Playlist so pode ser criada para cliente existente.
- Midia so pode ser vinculada a playlist do mesmo cliente.

## Autenticacao administrativa

- Endpoint: `POST /api/auth/login`.
- Variaveis Docker para seed local:
  - `MOVIPROGY_ADMIN_EMAIL`
  - `MOVIPROGY_ADMIN_PASSWORD`
- Tabelas:
  - `usuarios`
  - `admin_sessions`
- Token real e retornado apenas no login.
- Banco armazena somente hash do token.
- Senha nunca deve ser salva em texto puro.

## Simulacao local

- Pre-requisito: Docker Desktop aberto e daemon ativo.
- Subir backend: `docker compose up --build -d`.
- Rodar simulacao: `.\scripts\simulate_player.ps1`.
- Parar backend: `docker compose down`.

Pastas locais do projeto:
- `runtime/data`
- `runtime/media`
- `runtime/tmp`
- `logs`

Limite:
- Simulacao usa codigo demo `MOVI-DEMO-001`.
- Nao testa banco porque ainda nao ha banco definido.
- Docker Desktop ainda armazena imagens e cache no local global configurado no Docker.
- Persistencia JSON e apenas fallback sem banco.

Motivo:
- API REST leve.
- Boa documentacao OpenAPI.
- Testes simples com `TestClient`.
- Adequado para contratos do painel e player.

## Regras de continuidade

- Atualizar este arquivo sempre que uma escolha tecnica for aprovada.
- Nao substituir conhecimento historico; adicionar nova entrada com contexto.
- Se uma decisao mudar, registrar motivo e impacto.
