# PROJECT_RESUME.md

## Projeto

MoviProgy - Sistema Online de Midia Indoor com Sincronizacao Offline.

## Objetivo operacional

Permitir que administradores enviem campanhas de imagem e video para dispositivos remotos.
Os dispositivos devem sincronizar midias quando houver internet e manter reproducao local quando offline.

## Estado atual

- Pasta do projeto criada em `E:\Projetos\MoviProgy`.
- Documentacao inicial criada.
- `AGENTS.md` criado.
- Memoria permanente do projeto criada.
- Backend minimo criado com FastAPI.
- Endpoints iniciais: `GET /health` e `GET /api/system/info`.
- Dominio inicial de sincronizacao criado para validar manifesto por tamanho e hash.
- Contratos iniciais do player criados:
  - `POST /api/player/ativar`
  - `GET /api/player/playlist`
- Docker criado para executar o backend.
- Docker configurado com bind mounts em pastas do projeto para dados, midias, temporarios e logs.
- PostgreSQL adicionado ao Docker Compose com dados em `runtime/postgres/data`.
- Readiness do backend criado em `GET /health/ready`.
- Migration inicial criada para `device_sessions`.
- Migration core criada para `clientes`, `dispositivos`, `midias`, `playlists` e `playlist_midias`.
- Repository PostgreSQL core criado para persistir entidades iniciais do dominio.
- Rotas administrativas iniciais criadas para clientes e dispositivos.
- Rotas administrativas criadas para midias e playlists.
- Listagens administrativas criadas para clientes, dispositivos, midias e playlists.
- Listagens administrativas possuem `limit`, `offset` e filtros iniciais por status/cliente.
- Listagens administrativas retornam envelope paginado com `items`, `limit`, `offset` e `total`.
- Consulta administrativa de eventos do player criada por dispositivo.
- Vinculo administrativo de midia em playlist criado.
- Upload fisico local de midias criado em `POST /api/admin/midias/upload`.
- Autenticacao minima por `ADMIN_API_TOKEN` criada como fallback local legado.
- Login administrativo criado em `POST /api/auth/login`.
- Refresh de sessao administrativa criado em `POST /api/auth/refresh`.
- Logout administrativo criado em `POST /api/auth/logout`.
- RBAC minimo criado para `/api/admin/*` com perfil `admin`.
- RBAC granular inicial criado com vinculo usuario/cliente e permissoes `recurso:acao`.
- Endpoints administrativos de usuarios, vinculos e permissoes criados.
- Migration de auth criada para `usuarios` e `admin_sessions`.
- Migration RBAC criada para `usuarios_clientes` e `permissoes`.
- Auditoria de acessos administrativos criada para permissoes permitidas e negadas.
- Consulta administrativa de auditoria criada em `GET /api/admin/auditoria/acessos`.
- Politica de retencao de auditoria criada em `POST /api/admin/auditoria/retencao/executar`.
- Simulacao do player persiste sessoes no PostgreSQL quando executada via Docker.
- Ativacao do player usa `codigo_ativacao` real do banco quando disponivel.
- Manifesto do player usa `playlist_atual_id` do dispositivo e midias vinculadas quando disponivel.
- Download controlado de midia para player criado em `GET /api/player/midias/{midia_id}/download`.
- Consulta de atualizacao do player criada em `GET /api/player/atualizacao`.
- Telemetria do player criada:
  - `POST /api/player/status`
  - `POST /api/player/logs`
  - `POST /api/player/sincronizacao/confirmar`
- Script de simulacao do player criado.
- Escopo tecnico da integracao Google Drive documentado.
- Especificacao Google Drive / Armazenamento consolidada com UX/UI, OAuth, endpoints futuros e checklist.
- Implementacao inicial Google Drive criada com migrations, repository, OAuth, criptografia de tokens, pastas, importacao por metadados e tela administrativa.
- Integracao Google Drive corrigida para salvar pasta raiz por criacao/localizacao automatica no Drive, validar acesso, exibir feedback visual, consultar quota, enviar/importar arquivos e ocultar campos tecnicos do usuario.
- Especificacao completa do frontend documentada.
- RBAC granular planejado e documentado.
- Storage, upload e download controlado documentados.
- Especificacao do player real documentada.
- Deploy de producao, backup/restore e observabilidade documentados.
- Checklist de homologacao e matriz de testes documentados.
- Manual admin e manual operacional documentados.
- Repositorio Git inicializado localmente.
- Testes iniciais criados com pytest.
- Frontend inicial criado em `frontend/` com Vite, React e TypeScript.
- Login administrativo conectado em `POST /api/auth/login`.
- Logout conectado em `POST /api/auth/logout`.
- Tela de login redesenhada com identidade visual MoviProgy, mostrar/ocultar senha e placeholders desabilitados para recursos sem contrato backend.
- Painel autenticado criado com sidebar, header e navegacao.
- Layout autenticado refinado com sidebar escura, topbar com busca e perfil lateral.
- Dashboard redesenhado com cards analiticos, eventos de auditoria e alertas derivados dos dados reais da API.
- Tela de Clientes redesenhada como gestao operacional com KPIs reais, busca local, filtro por status, cadastro e dispositivos vinculados.
- Tela de Dispositivos redesenhada como gestao de frota com KPIs, busca local, cadastro e tabela detalhada.
- Cadastro de dispositivo gera ID sequencial por nome e codigo de ativacao automaticamente.
- Telas iniciais criadas para Dashboard, Clientes, Dispositivos, Midias, Playlists, Logs/Auditoria, Usuarios, Sincronizacoes, Google Drive e Configuracoes.
- Listagens iniciais consomem endpoints paginados do backend.
- Edicao administrativa criada para clientes, dispositivos, midias e playlists.
- Editor de playlist permite listar, vincular e remover midias, com incremento de versao.
- Consulta administrativa de sincronizacoes criada em `GET /api/admin/sincronizacoes`.
- Tela de sincronizacoes conectada a confirmacoes reais dos players.
- Tela de configuracoes exibe somente parametros operacionais seguros do backend.
- Upload local de midia, criacao/publicacao de playlists e criacao/inativacao de usuarios foram conectados no frontend.
- Gestao de usuarios permite consultar e criar vinculos com clientes e conceder permissoes por recurso, acao e escopo.
- Infraestrutura de testes do frontend criada com Vitest e Testing Library.
- E2E do painel criado com Playwright para login, dashboard, navegacao e logout.
- Frontend empacotado em container Nginx com proxy para a API e health check proprio.
- Compose integrado publica o painel em `http://127.0.0.1:8080`.
- Credenciais de desenvolvimento foram removidas dos valores iniciais da tela de login.
- Smoke test integrado criado para frontend, health, readiness, login, rota protegida e logout.
- Smoke de carga local criado para frontend, player, health, readiness e listagem autenticada.
- Proxy do frontend encaminha `/health` e `/health/ready` para a API.
- Middleware de observabilidade registra requisicoes HTTP em JSON e retorna `X-Request-ID`.
- Logs estruturados nao incluem Authorization, corpo ou credenciais.
- Backup automatizado gera dump PostgreSQL, copia midias e cria manifesto com checksum.
- Restore automatizado foi validado em banco temporario isolado.
- CI criado para backend com PostgreSQL real e frontend com testes/build.
- Estrategia de ambientes criada com dados, banco, logs, storage, configuracoes e Compose isolados para DEV e PROD.
- Branch `develop` definida para deploy automatico DEV apos CI.
- Branch `main` definida para PROD com tag, confirmacao e aprovacao.
- Scripts remotos de deploy, smoke, backup e rollback criados.
- VPS preparada com Docker, Compose, usuario de deploy, firewall e fail2ban.
- API desabilita documentacao publica em PROD e valida hosts permitidos.
- Ambiente DEV publicado e homologado em `http://172.233.177.135:8081`.
- Player DEV publicado e homologado em `http://172.233.177.135:8092`.
- Resultado registrado em `docs/15-homologacao/resultado-dev-2026-06-06.md`.
- Ambiente PROD permanece sem containers e bloqueado no servidor.
- Manifesto do player inclui `media_id`, tipo e duracao para permitir download e reproducao pelo player real.
- Design do player PWA offline-first registrado e implementado conforme `docs/superpowers/specs/2026-06-06-player-pwa-design.md`.

## Arquivos principais

- `README.md`
- `AGENTS.md`
- `PROJECT_RESUME.md`
- `LESSONS_LEARNED.md`
- `KNOWLEDGE_BASE.md`
- `ARCHITECTURE_DECISIONS.md`
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

## Decisoes ja assumidas

- Documentar antes de codificar.
- Player deve ser offline-first.
- Sincronizacao deve preservar a ultima playlist valida.
- Nova playlist so substitui a antiga apos validacao completa.
- Toda decisao critica deve ficar no projeto, nao em memoria externa.
- Frontend so deve iniciar apos fechamento do backend.
- Stack frontend MVP: Vite + React + TypeScript.

## Pendencias externas

- Credenciais reais Google Drive para nova homologacao externa, se a conta configurada for alterada.
- Dominio e certificados HTTPS para producao.
- Aprovacao explicita para ativar `PRODUCTION_APPROVED=true`.
- Ampliacao da VPS antes de executar DEV e PROD simultaneamente.

## Limitacoes atuais

- Manifesto demo permanece apenas como fallback sem playlist real no banco.
- Codigo de ativacao demo `MOVI-DEMO-001` funciona apenas sem repository/banco.
- Hash do token do dispositivo e persistido no PostgreSQL quando `DATABASE_URL` esta configurado.
- JSON local permanece apenas como fallback sem banco.
- Docker atual sobe frontend, backend e PostgreSQL.
- Docker Desktop ainda pode usar armazenamento global fora do projeto para imagens/cache.
- Simulacao atual cobre ativacao e consulta de manifesto.
- Rotas administrativas atuais exigem sessao de usuario admin quando `auth_repository` esta disponivel.
- `ADMIN_API_TOKEN` permanece apenas como fallback legado sem banco.
- Perfil legado `admin` possui acesso total.
- Perfis escopados dependem de vinculo com cliente e permissao por recurso/acao.
- Auditoria de acessos RBAC registra permissoes permitidas e negadas, sem gravar tokens.
- Edicao de item de playlist ainda usa remocao e nova inclusao; endpoint `PATCH` do item nao foi criado.
- Manifesto real depende de `dispositivos.playlist_atual_id`, playlist ativa e midias vinculadas.
- Download controlado atual serve arquivo local de `MOVIPROGY_MEDIA_DIR`.
- Google Drive possui implementacao inicial em `/api/integrations/google-drive`.
- Pasta raiz do Google Drive e criada/localizada automaticamente pelo backend e validada antes de atualizar a interface.
- Metadados tecnicos do Drive ficam ocultos no frontend e sao preenchidos pelo backend quando o arquivo e importado.
- Fluxo real depende de `MOVIPROGY_GOOGLE_CLIENT_ID`, `MOVIPROGY_GOOGLE_CLIENT_SECRET`, `MOVIPROGY_GOOGLE_REDIRECT_URI` e `MOVIPROGY_GOOGLE_TOKEN_KEY`.
- Sem credenciais Google, a tela opera com status e simulacao local controlada, mas nao autentica conta real.
- Script `scripts/configure_google_oauth.ps1` cria `.env` local para OAuth real ou simulacao.
- Player PWA offline-first implementado em `player/`.
- Player persiste dispositivo, manifesto, midias e telemetria em IndexedDB.
- Player valida tamanho e SHA-256 antes de promover uma playlist.
- Player preserva a playlist ativa quando API ou download falham.
- Service worker mantém o shell do player disponível offline.
- Container `moviprogy-player` publicado localmente em `http://127.0.0.1:8091`.
- Homologacao real executada com ativacao, download, reproducao, reinicio sem API e recuperacao.

## Proximo passo recomendado

Backend administrativo e frontend operacional consolidados.

Pendencias prioritarias:
- Testes de carga reais em volume de producao continuam recomendados antes de deploy publico.
- Definir dominio, HTTPS e monitoramento do ambiente de producao.
- Executar homologacao de producao somente apos aprovacao.
