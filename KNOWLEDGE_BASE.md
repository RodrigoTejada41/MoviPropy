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
- Frontend MVP definido: Vite + React + TypeScript.
- Testes definidos: pytest com FastAPI TestClient.
- Documentacao funcional, tecnica, operacional e de homologacao foi fechada como baseline antes de continuar backend/frontend.
- Banco definido para ambiente Docker local: PostgreSQL.
- Contratos iniciais do player persistem sessoes no PostgreSQL quando `DATABASE_URL` existe.
- Contratos do player consultam dispositivo e manifesto real no PostgreSQL quando `core_repository` existe.
- Login administrativo persiste sessoes no PostgreSQL quando `DATABASE_URL` existe.
- Refresh/logout administrativo invalidam tokens antigos em `admin_sessions`.
- Docker Compose executa o backend em `moviprogy-api`.
- Docker Compose executa PostgreSQL em `moviprogy-db`.
- Dados de runtime do container devem usar bind mounts em `runtime/` e `logs/` dentro do projeto.
- Storage local inicial definido em `MOVIPROGY_MEDIA_DIR`.
- Google Drive possui implementacao inicial de storage externo controlado pelo backend.
- Google Drive / Armazenamento possui UX/UI, OAuth, endpoints, dados, seguranca, quota e testes iniciais.
- Google Drive nao deve expor IDs, tokens, links internos, MIME, tamanho ou hash como campos manuais no frontend.
- Pasta raiz do Google Drive deve ser criada/localizada automaticamente pela API Google Drive e persistida no banco pelo backend.
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
- Listagens administrativas retornam envelope paginado com `items`, `limit`, `offset` e `total`.
- Tabelas `usuarios` e `admin_sessions` implementam login administrativo inicial.
- Tabelas `usuarios_clientes` e `permissoes` implementam RBAC granular inicial.
- Endpoints administrativos gerenciam usuarios, vinculos com clientes e permissoes.
- Tabela `auditoria_acessos` registra tentativas administrativas permitidas e negadas.
- Retencao de auditoria usa endpoint administrativo com default de 180 dias.
- Backend deve chegar a 100% antes de iniciar frontend.

## Integracao Google Drive

- Documento principal: `docs/09-google-drive/integracao-google-drive.md`.
- Namespace canonico: `/api/integrations/google-drive`.
- Implementacao atual cobre status, connect, callback, disconnect, folders, root-folder, client-folder, files, import-media, upload-media e validate-access.
- `POST /api/integrations/google-drive/root-folder` localiza ou cria a pasta raiz no Drive, salva o ID real no banco, valida acesso e registra operacao.
- `POST /api/integrations/google-drive/import-media` busca metadados tecnicos do arquivo no backend; o frontend informa apenas cliente, tipo e arquivo selecionado.
- `POST /api/integrations/google-drive/upload-media` envia arquivo ao Drive e salva metadados automaticamente sem limite manual no frontend.
- OAuth real depende de variaveis Google Cloud.
- `MOVIPROGY_GOOGLE_TOKEN_KEY` e obrigatoria para criptografar tokens no callback.
- `MOVIPROGY_GOOGLE_OAUTH_SIMULATED=true` permite simulacao local de callback sem chamar Google.
- Script local: `scripts/configure_google_oauth.ps1`.
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
- Frontend/Admin: Vite, React e TypeScript.
- Testes backend: pytest.
- Servidor ASGI: uvicorn.

## Frontend administrativo

- Codigo: `frontend/`.
- Servidor local: `npm run dev` em `frontend/`.
- Build: `npm run build`.
- Login usa `POST /api/auth/login`.
- Logout usa `POST /api/auth/logout`.
- Tela de login possui layout visual proprio, sem Tailwind CDN e sem scripts inline.
- Recuperacao de senha e SSO aparecem desabilitados enquanto nao houver contrato backend.
- Token admin fica no `localStorage` como solucao MVP local.
- API local usa proxy do Vite para `http://127.0.0.1:8000`.
- Telas implementadas inicialmente:
  - Dashboard com cards analiticos, auditoria e alertas derivados de dados reais.
  - Clientes com layout de gestao, KPIs reais, busca local, filtro por status, cadastro e contagem de dispositivos vinculados.
  - Dispositivos com layout de frota, KPIs, busca local e cadastro.
  - Midias.
  - Playlists.
  - Logs/Auditoria.
  - Usuarios e permissoes.
  - Sincronizacoes com placeholder por falta de endpoint especifico.
  - Google Drive / Armazenamento com status, OAuth, quota, pastas e importacao por arquivo selecionado.
  - Configuracoes com placeholder por falta de endpoints.
- A tela de dispositivos nao deve inventar ultima comunicacao; enquanto a API nao retorna esse campo, mostrar `Nao informado`.
- A tela de clientes nao deve inventar regiao, data de criacao ou ultimo sync; enquanto a API nao retorna esses campos, mostrar `Nao informado` ou deixar a acao desabilitada.
- O dashboard nao deve inventar numeros de infraestrutura; deve calcular indicadores a partir de clientes, dispositivos, midias, playlists e auditoria.

## Contratos atuais do player

- `POST /api/player/ativar`: ativa dispositivo por codigo e retorna token.
- `GET /api/player/playlist`: retorna manifesto ativo mediante token Bearer.
- `GET /api/player/atualizacao`: compara versao local com versao da playlist ativa.
- `POST /api/player/status`: registra status operacional do dispositivo.
- `POST /api/player/logs`: registra evento/log enviado pelo dispositivo.
- `POST /api/player/sincronizacao/confirmar`: registra resultado de sincronizacao.

Implementacao atual:
- Ativacao real usa `dispositivos.codigo_ativacao`.
- Dispositivo bloqueado nao ativa pelo fluxo real.
- Manifesto real usa `dispositivos.playlist_atual_id`.
- Playlist precisa estar ativa.
- Arquivos do manifesto sao gerados por `playlist_midias` ordenado por `ordem`.
- Somente midias ativas entram no manifesto.

Limite:
- Manifesto demo ainda existe apenas como fallback sem repository/banco.
- Sessoes do player usam PostgreSQL quando `DATABASE_URL` existe.
- JSON e apenas fallback para execucao sem banco.
- Upload fisico local existe em `POST /api/admin/midias/upload`.
- Download controlado implementado em `GET /api/player/midias/{midia_id}/download`.
- Download so libera midia ativa vinculada a playlist atual ativa do dispositivo.
- Telemetria do player persiste eventos em PostgreSQL quando `DATABASE_URL` existe.

Persistencia atual:
- Tabela: `device_sessions`.
- Tabelas core: `clientes`, `dispositivos`, `midias`, `playlists`, `playlist_midias`.
- Tabelas de telemetria: `player_status_events`, `player_log_events`, `player_sync_confirmations`.
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
- `GET /api/admin/clientes`
- `GET /api/admin/clientes/{cliente_id}`
- `PATCH /api/admin/clientes/{cliente_id}`
- `POST /api/admin/dispositivos`
- `GET /api/admin/dispositivos`
- `GET /api/admin/dispositivos/{dispositivo_id}`
- `PATCH /api/admin/dispositivos/{dispositivo_id}`
- `GET /api/admin/dispositivos/{dispositivo_id}/eventos`
- `POST /api/admin/midias`
- `POST /api/admin/midias/upload`
- `GET /api/admin/midias`
- `GET /api/admin/midias/{midia_id}`
- `PATCH /api/admin/midias/{midia_id}`
- `POST /api/admin/playlists`
- `GET /api/admin/playlists`
- `GET /api/admin/playlists/{playlist_id}`
- `PATCH /api/admin/playlists/{playlist_id}`
- `POST /api/admin/playlists/{playlist_id}/midias`
- `GET /api/admin/playlists/{playlist_id}/midias`
- `DELETE /api/admin/playlists/{playlist_id}/midias/{midia_id}`
- `GET /api/admin/sincronizacoes`
- `GET /api/admin/configuracoes`
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

Seguranca:
- Exigem `Authorization: Bearer <access_token>` retornado por `POST /api/auth/login`.
- Perfil legado `admin` possui acesso total.
- Perfis escopados precisam de vinculo em `usuarios_clientes` e permissao em `permissoes`.
- `ADMIN_API_TOKEN` existe apenas como fallback local quando `auth_repository` nao esta disponivel.

Limite:
- Sessao admin usa hash SHA-256 do token no banco.
- Senha usa PBKDF2-HMAC-SHA256 com salt individual.

Regras de negocio atuais:
- Midia so pode ser criada para cliente existente.
- Playlist so pode ser criada para cliente existente.
- Midia so pode ser vinculada a playlist do mesmo cliente.
- Listagens administrativas aceitam `limit`, `offset` e filtros iniciais.
- Clientes filtram por `ativo`.
- Dispositivos filtram por `cliente_id` e `bloqueado`.
- Midias filtram por `cliente_id` e `ativo`.
- Playlists filtram por `cliente_id` e `ativa`.
- Resposta das listagens usa envelope paginado com `items`, `limit`, `offset` e `total`.
- Alteracao de playlist e inclusao/remocao de midia incrementam a versao.
- Manifesto retorna `media_id`, nome, tipo, tamanho, hash e duracao.
- Configuracoes administrativas retornam somente provider, limite efetivo de upload e modo offline-first.

## Autenticacao administrativa

- Endpoint: `POST /api/auth/login`.
- Endpoint: `POST /api/auth/refresh`.
- Endpoint: `POST /api/auth/logout`.
- Variaveis Docker para seed local:
  - `MOVIPROGY_ADMIN_EMAIL`
  - `MOVIPROGY_ADMIN_PASSWORD`
- Tabelas:
  - `usuarios`
  - `admin_sessions`
- Token real e retornado apenas no login ou refresh.
- Refresh retorna novo token e remove token anterior.
- Logout remove a sessao atual.
- Banco armazena somente hash do token.
- Senha nunca deve ser salva em texto puro.
- Permissoes usam formato `recurso:acao`, com escopo opcional por `cliente_id`.
- Usuario escopado sem `cliente_id` em listagens de dados por cliente recebe 403.
- Auditoria administrativa registra `user_id`, `cliente_id`, `recurso`, `acao`, `status`, IP e user-agent.
- Auditoria administrativa nao registra token Bearer nem senha.

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
- Simulacao sem banco usa codigo demo `MOVI-DEMO-001`.
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

## Observabilidade HTTP

- Logger: `moviprogy.request`.
- Formato JSON em uma linha.
- Campos: `event`, `request_id`, `method`, `path`, `status_code`, `duration_ms`.
- Resposta inclui `X-Request-ID`.
- Nao registrar Authorization, cookies, corpo ou query sensivel.

## Backup local

- Criar com `scripts/backup_stack.ps1`.
- Validar com `scripts/test_restore.ps1`.
- Dumps e midias ficam em `backups/`, fora do Git.
- O teste de restore usa banco temporario e nunca sobrescreve `moviprogy`.
