# Matriz de Testes

## Objetivo

Mapear funcionalidades, tipos de teste e status esperado.

| Funcionalidade | Unitario | Integracao | Funcional | Seguranca | Performance | Status |
|---|---|---|---|---|---|---|
| Health | Sim | Sim | Sim | Nao | Sim | Implementado |
| Readiness | Sim | Sim | Sim | Nao | Sim | Implementado |
| Login admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| RBAC admin | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Clientes | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Dispositivos | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Midias metadados | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Playlists | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Vinculo playlist/midia | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Manifesto player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Atualizacao player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Upload midia | Sim | Pendente | Sim | Sim | Pendente | Implementado parcial |
| Download player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Status player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Logs player | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Confirmacao sincronizacao | Sim | Sim | Sim | Sim | Pendente | Implementado parcial |
| Google Drive | Pendente | Pendente | Pendente | Pendente | Pendente | Pendente |
| Frontend login | Pendente | Pendente | Pendente | Pendente | Pendente | Pendente |
| Frontend playlists | Pendente | Pendente | Pendente | Pendente | Pendente | Pendente |

## Regras

- Toda funcionalidade nova deve ter teste minimo.
- Bug corrigido deve gerar teste de regressao.
- Teste real de banco depende de `DATABASE_URL`.
- Teste offline do player e obrigatorio antes de homologacao.
