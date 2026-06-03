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
- Storage.
- Deploy.
- RBAC granular por cliente/acao.
- Download controlado de midias para player.

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
