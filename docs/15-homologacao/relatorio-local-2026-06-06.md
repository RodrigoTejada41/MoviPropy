# Relatorio de Homologacao Local

Data: 2026-06-06

## Escopo

- Backend FastAPI.
- PostgreSQL.
- Painel administrativo.
- Google Drive OAuth real.
- Player PWA offline-first.
- Docker Compose local.

## Resultados

- Backend: 89 testes aprovados e 10 testes PostgreSQL condicionais ignorados sem ambiente dedicado.
- Frontend: 10 testes aprovados e build aprovado.
- Player: 15 testes aprovados e build aprovado.
- Smoke integrado: frontend, player, API, banco, login, rota protegida e logout aprovados.
- Backup e restore: dump com checksum restaurado em banco temporario com 19 tabelas.
- Google Drive: OAuth, acesso, pasta raiz e consulta aprovados.
- Player online: ativacao, manifesto, download, hash, reproducao e telemetria aprovados.
- Player offline: recarga sem API preservou e reproduziu a playlist do IndexedDB.
- Responsividade: 1920x1080 e 390x844 sem overflow.

## Evidencias operacionais

- Painel: `http://127.0.0.1:8080`.
- API: `http://127.0.0.1:8000`.
- Player: `http://127.0.0.1:8091`.
- Smoke: `scripts/smoke_stack.ps1`.

## Pendencias externas para producao

- Dominio e certificado HTTPS.
- Provedor de infraestrutura.
- Storage e politica de backup de producao.
- Monitoramento externo e alertas.
- Testes de carga com volume real.
