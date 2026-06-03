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
- RBAC granular por cliente/acao.

## D-002 - Login administrativo antes de Google Drive

Status: aprovado.

Decisao:
- Criar login administrativo e RBAC minimo antes de implementar Google Drive.

Motivo:
- Google Drive exige credenciais sensiveis.
- Rotas administrativas nao podem depender apenas de token global.

Impacto:
- `/api/admin/*` passa a exigir usuario com perfil `admin`.
- `ADMIN_API_TOKEN` fica como fallback legado local.

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
