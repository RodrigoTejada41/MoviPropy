# Decisoes tecnicas

## D-001 - Projeto documentado antes do codigo

Status: aprovado.

Decisao:
- Criar documentacao inicial e `AGENTS.md` antes de qualquer codigo-fonte.

Motivo:
- O projeto estava vazio.
- O escopo exige aprovacao antes de alteracoes.

Impacto:
- Reduz risco de implementacao sem arquitetura.
- Cria rastreabilidade inicial.

## Pendentes

- Frontend.
- Storage externo.
- Deploy.
- Fechamento backend 100%.

## D-002 - Login administrativo antes de Google Drive

Status: aprovado.

Decisao:
- Criar login administrativo e RBAC minimo antes de implementar Google Drive.

Motivo:
- Google Drive exige credenciais sensiveis.
- Rotas administrativas nao podem depender apenas de token global.

Impacto:
- `/api/admin/*` passa a exigir usuario autenticado.
- `ADMIN_API_TOKEN` fica como fallback legado local.
- RBAC granular foi definido depois na D-011.

## D-003 - Manifesto real do player

Status: aprovado.

Decisao:
- Player deve receber manifesto real quando o dispositivo tiver playlist atual ativa no banco.

Motivo:
- Remove dependencia do manifesto demo no fluxo com PostgreSQL.
- Permite testar sincronizacao com dados reais.

Impacto:
- `GET /api/player/playlist` usa midias vinculadas a playlist atual.
- Demo permanece apenas como fallback local.

## D-004 - Fechamento documental antes de backend/frontend

Status: aprovado.

Decisao:
- Completar documentacao funcional, tecnica, operacional e de homologacao antes de continuar implementacao.

Motivo:
- Reduz retrabalho.
- Evita implementar frontend sem mapa de telas.
- Evita backend sem regras de storage, RBAC, deploy e homologacao.

Impacto:
- Proxima fase pode focar em backend.
- Frontend deve seguir `docs/10-frontend/especificacao-frontend.md`.
- Homologacao deve seguir `docs/15-homologacao/checklist-homologacao.md`.

## D-005 - Download controlado pelo backend

Status: aprovado.

Decisao:
- Player baixa midias por endpoint do backend, nao por caminho direto.

Motivo:
- Controlar permissao por dispositivo.
- Evitar exposicao de storage.
- Preservar operacao offline com arquivo local no player.

Impacto:
- `GET /api/player/midias/{midia_id}/download` valida token e playlist atual.
- Upload fisico foi definido depois na D-006.

## D-006 - Upload fisico local de midias

Status: aprovado.

Decisao:
- Admin pode enviar arquivo por `POST /api/admin/midias/upload`.
- Backend gera caminho relativo e calcula hash SHA-256.

Motivo:
- Fechar fluxo minimo upload -> playlist -> download.
- Evitar caminho fisico informado pelo usuario.

Impacto:
- Arquivos ficam sob `MOVIPROGY_MEDIA_DIR`.
- Storage externo continua pendente para escala.

## D-007 - Telemetria do player

Status: aprovado.

Decisao:
- Player envia status, logs e confirmacao de sincronizacao para o backend.

Motivo:
- Permitir monitoramento de dispositivos.
- Registrar falhas e sucesso de sincronizacao.

Impacto:
- Criadas tabelas `player_status_events`, `player_log_events` e `player_sync_confirmations`.
- Listagens administrativas de eventos foram definidas depois na D-009.

## D-008 - Consulta de atualizacao do player

Status: aprovado.

Decisao:
- Player consulta `GET /api/player/atualizacao` para comparar sua versao local com a playlist ativa.

Motivo:
- Reduz trafego.
- Evita baixar manifesto completo sem necessidade.

Impacto:
- Player recebe `possui_atualizacao` e `nova_versao`.
- Se houver atualizacao, o player deve buscar `GET /api/player/playlist`.

## D-009 - Listagens administrativas iniciais

Status: aprovado.

Decisao:
- Criar listagens administrativas para clientes, dispositivos, midias e playlists.
- Criar consulta de eventos por dispositivo.

Motivo:
- Desbloquear telas principais do painel.
- Permitir monitorar eventos do player.

Impacto:
- Rotas ficam protegidas por sessao admin.
- Paginacao e filtros foram definidos depois na D-010.
- Isolamento granular por cliente foi definido depois na D-011.

## D-010 - Paginacao e filtros administrativos

Status: aprovado.

Decisao:
- Listagens administrativas devem aceitar `limit`, `offset` e filtros basicos.
- O formato de resposta permaneceu lista simples na etapa inicial.

Motivo:
- Reduzir risco de consultas grandes antes do frontend.
- Manter compatibilidade com contratos iniciais.

Impacto:
- Clientes filtram por `ativo`.
- Dispositivos filtram por `cliente_id` e `bloqueado`.
- Midias filtram por `cliente_id` e `ativo`.
- Playlists filtram por `cliente_id` e `ativa`.
- `total` para paginacao completa foi definido depois na D-014.

## D-011 - RBAC granular por cliente e acao

Status: aprovado.

Decisao:
- Manter perfil legado `admin` com acesso total.
- Validar perfis escopados por vinculo de cliente e permissao `recurso:acao`.
- Criar tabelas `usuarios_clientes` e `permissoes`.

Motivo:
- Garantir isolamento multi-cliente.
- Preparar perfis operacionais antes do frontend.

Impacto:
- Usuario escopado sem permissao recebe 403.
- Usuario escopado sem vinculo com cliente recebe 403.
- Listagens por dados de cliente exigem `cliente_id` para usuario escopado.
- Auditoria de acessos foi definida depois na D-012.

## D-012 - Auditoria de acessos administrativos

Status: aprovado.

Decisao:
- Registrar acessos administrativos permitidos e negados.
- Persistir `user_id`, `cliente_id`, `recurso`, `acao`, `status`, IP e user-agent.
- Nao persistir token Bearer nem senha.

Motivo:
- Rastrear decisoes de autorizacao.
- Apoiar investigacao de acesso indevido.

Impacto:
- Criada tabela `auditoria_acessos`.
- Fluxo central de permissao administrativa registra auditoria.
- Endpoint de consulta de auditoria foi definido depois na D-013.

## D-013 - Backend 100% antes do frontend

Status: aprovado.

Decisao:
- Nao iniciar frontend antes do fechamento backend.
- Priorizar contratos, seguranca, auditoria, paginacao completa, usuarios/permissoes e homologacao backend.

Motivo:
- Evitar retrabalho de telas com API instavel.
- Fechar base tecnica antes da interface.

Impacto:
- Frontend fica bloqueado ate nova decisao.
- Backlog backend passa a ter prioridade total.

## D-014 - Envelope paginado administrativo

Status: aprovado.

Decisao:
- Listagens administrativas retornam `items`, `limit`, `offset` e `total`.
- O `total` usa os mesmos filtros da consulta.

Motivo:
- Fechar contrato de paginacao antes do frontend.
- Evitar que o painel precise carregar todos os registros.

Impacto:
- Contrato antigo de lista simples foi substituido.
- Frontend deve ler dados em `items`.
- Testes de performance devem considerar consulta de contagem.

## D-015 - Gestao backend de usuarios e permissoes

Status: aprovado.

Decisao:
- Criar endpoints administrativos para usuarios, vinculos com clientes e permissoes.
- Nao retornar senha nem hash em respostas.
- Exigir permissoes `usuarios:*`.

Motivo:
- Fechar RBAC operacional antes do frontend.
- Evitar manutencao manual no banco.

Impacto:
- Backend passa a expor contratos para tela de usuarios.
- Frontend deve usar `/api/admin/usuarios`.
- Refresh/logout de sessao continua pendente.
