# Matriz de Testes

## Objetivo

Mapear funcionalidades, tipos de teste e status esperado.

| Funcionalidade | Unitario | Integracao | Funcional | Seguranca | Performance | Status |
|---|---|---|---|---|---|---|
| Health | Sim | Sim | Sim | Nao | Sim | Implementado e carga local aprovada |
| Readiness | Sim | Sim | Sim | Nao | Sim | Implementado e carga local aprovada |
| Login admin | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Refresh/logout admin | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Gestao usuarios/permissoes | Sim | Sim | Sim | Sim | Pendente | Implementado |
| RBAC admin | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| RBAC granular cliente/acao | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Auditoria admin | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Consulta auditoria admin | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Retencao auditoria admin | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Clientes | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Dispositivos | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Midias metadados | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Playlists | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Listagens admin com total | Sim | Sim | Sim | Sim | Sim | Implementado e carga local aprovada |
| Eventos player admin | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Vinculo playlist/midia | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Manifesto player | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Atualizacao player | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Upload midia | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Download player | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Status player | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Logs player | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Confirmacao sincronizacao | Sim | Sim | Sim | Sim | Pendente | Implementado e testado |
| Google Drive especificacao | Nao | Nao | Revisao documental | Revisao documental | Nao | Documentado |
| Google Drive | Sim | Sim | Sim | Sim | Pendente | Homologado local |
| Google Drive OAuth real | Sim | Sim | Sim | Sim | Pendente | Homologado local |
| Frontend login | Sim | Sim | Sim | Sim | Pendente | E2E aprovado |
| Frontend dashboard/listagens | Sim | Sim | Sim | Parcial | Pendente | E2E basico aprovado |
| Frontend playlists | Sim | Sim | Sim | Parcial | Pendente | Implementado |
| Frontend sincronizacoes/configuracoes | Sim | Sim | Sim | Parcial | Pendente | Implementado |
| Player PWA ativacao | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Player PWA IndexedDB | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Player PWA offline | Sim | Sim | Sim | Sim | Pendente | Homologado local |
| Player PWA telemetria | Sim | Sim | Sim | Sim | Pendente | Implementado |

## Regras

- Toda funcionalidade nova deve ter teste minimo.
- Bug corrigido deve gerar teste de regressao.
- Teste real de banco depende de `DATABASE_URL`.
- Testes do frontend executam com `cd frontend; npm test`.
- E2E do frontend executa com `cd frontend; npm run test:e2e`.
- Smoke de carga executa com `py -3 scripts/load_smoke.py --requests 100 --concurrency 10`.
- Teste offline do player e obrigatorio antes de homologacao.
