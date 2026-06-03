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
- Vinculo administrativo de midia em playlist criado.
- Autenticacao minima por `ADMIN_API_TOKEN` criada como fallback local legado.
- Login administrativo criado em `POST /api/auth/login`.
- RBAC minimo criado para `/api/admin/*` com perfil `admin`.
- Migration de auth criada para `usuarios` e `admin_sessions`.
- Simulacao do player persiste sessoes no PostgreSQL quando executada via Docker.
- Ativacao do player usa `codigo_ativacao` real do banco quando disponivel.
- Manifesto do player usa `playlist_atual_id` do dispositivo e midias vinculadas quando disponivel.
- Script de simulacao do player criado.
- Escopo tecnico da integracao Google Drive documentado.
- Repositorio Git inicializado localmente.
- Testes iniciais criados com pytest.

## Arquivos principais

- `README.md`
- `AGENTS.md`
- `PROJECT_RESUME.md`
- `LESSONS_LEARNED.md`
- `KNOWLEDGE_BASE.md`
- `ARCHITECTURE_DECISIONS.md`

## Decisoes ja assumidas

- Documentar antes de codificar.
- Player deve ser offline-first.
- Sincronizacao deve preservar a ultima playlist valida.
- Nova playlist so substitui a antiga apos validacao completa.
- Toda decisao critica deve ficar no projeto, nao em memoria externa.

## Pendencias de aprovacao

- Stack frontend.
- RBAC granular por permissao/cliente.
- Tecnologia do player.
- Implementacao da integracao Google Drive.

## Limitacoes atuais

- Manifesto demo permanece apenas como fallback sem playlist real no banco.
- Codigo de ativacao demo: `MOVI-DEMO-001`.
- Hash do token do dispositivo e persistido no PostgreSQL quando `DATABASE_URL` esta configurado.
- JSON local permanece apenas como fallback sem banco.
- Docker atual sobe backend e PostgreSQL.
- Docker Desktop ainda pode usar armazenamento global fora do projeto para imagens/cache.
- Simulacao atual cobre ativacao e consulta de manifesto.
- Rotas administrativas atuais exigem sessao de usuario admin quando `auth_repository` esta disponivel.
- `ADMIN_API_TOKEN` permanece apenas como fallback legado sem banco.
- RBAC atual diferencia apenas perfil `admin`; ainda falta permissao granular por cliente/acao.
- Rotas de midias/playlists ainda sao CRUD inicial; nao fazem upload fisico.
- Manifesto real depende de `dispositivos.playlist_atual_id`, playlist ativa e midias vinculadas.
- Google Drive esta documentado como plano, mas ainda nao possui codigo, migration, OAuth ou endpoints reais.

## Proximo passo recomendado

Criar upload de midias ou endpoint de download controlado para o player.
