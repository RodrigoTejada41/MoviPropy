# Matriz de Testes

## Objetivo

Mapear funcionalidades, tipos de teste e status esperado.

| Funcionalidade | Unitario | Integracao | Funcional | Seguranca | Performance | Status |
|---|---|---|---|---|---|---|
| Health | Sim | Sim | Sim | Nao | Sim | Implementado |
| Readiness | Sim | Sim | Sim | Nao | Sim | Implementado |
| Login admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Refresh/logout admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Gestao usuarios/permissoes | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
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
| Google Drive OAuth real | Pendente | Pendente | Pendente | Pendente | Pendente | Pendente credenciais Google |
| Frontend login | Build | Pendente | Parcial | Pendente | Pendente | Implementado parcial |
| Frontend dashboard/listagens | Build | Pendente | Sim | Pendente | Pendente | Implementado parcial |
| Frontend playlists | Build | Pendente | Sim | Pendente | Pendente | Implementado parcial |
| Frontend sincronizacoes/configuracoes | Build | Pendente | Sim | Pendente | Pendente | Implementado parcial |

## Regras

- Toda funcionalidade nova deve ter teste minimo.
- Bug corrigido deve gerar teste de regressao.
- Teste real de banco depende de `DATABASE_URL`.
- Teste offline do player e obrigatorio antes de homologacao.
