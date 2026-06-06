# Matriz de Testes

## Objetivo

Mapear funcionalidades, tipos de teste e status esperado.

| Funcionalidade | Unitario | Integracao | Funcional | Seguranca | Performance | Status |
|---|---|---|---|---|---|---|
| Health | Sim | Sim | Sim | Nao | Sim | Implementado |
| Readiness | Sim | Sim | Sim | Nao | Sim | Implementado |
| Login admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Refresh/logout admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Gestao usuarios/permissoes | Sim | Sim | Sim | Sim | Pendente | Implementado |
| RBAC admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| RBAC granular cliente/acao | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Auditoria admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Consulta auditoria admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Retencao auditoria admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Clientes | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Dispositivos | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Midias metadados | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Playlists | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Listagens admin com total | Sim | Sim | Sim | Sim | Parcial | Implementado parcial |
| Eventos player admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Vinculo playlist/midia | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Manifesto player | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Atualizacao player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Upload midia | Sim | Pendente | Sim | Sim | Pendente | Implementado parcial |
| Download player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Status player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Logs player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Confirmacao sincronizacao | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Google Drive especificacao | Nao | Nao | Revisao documental | Revisao documental | Nao | Documentado |
| Google Drive implementacao inicial | Sim | Sim | Parcial | Sim | Pendente | Implementado parcial |
| Google Drive OAuth real | Sim | Sim | Sim | Sim | Pendente | Homologado local |
| Frontend login | Sim | Sim | Sim | Sim | Pendente | Implementado |
| Frontend dashboard/listagens | Sim | Sim | Sim | Parcial | Pendente | Implementado |
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
- Teste offline do player e obrigatorio antes de homologacao.
