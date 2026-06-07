# Plano de deploy

## Infraestrutura minima

- VPS ou cloud.
- HTTPS obrigatorio.
- Banco PostgreSQL ou MySQL.
- Storage local no MVP ou storage externo.
- Backup automatico.
- Monitoramento de disco.
- Health check da API.

## Ambientes

- Desenvolvimento local.
- Homologacao.
- Producao.

## Processo

1. Validar testes.
2. Gerar backup.
3. Aplicar migracoes.
4. Publicar backend.
5. Publicar frontend.
6. Validar storage.
7. Validar HTTPS.
8. Executar smoke tests.
9. Monitorar logs.

## Integracao continua

Workflow:
- `.github/workflows/ci.yml`.

Validacoes:
- Backend Python 3.12 com PostgreSQL 16 real.
- Suite completa `pytest`.
- Frontend Node 22 com `npm ci`.
- Testes Vitest.
- E2E Playwright em Chromium.
- Build Vite/TypeScript.
- Player Node 22 com Vitest e build Vite/TypeScript.

## Execucao local com Docker

Subir backend:

```powershell
docker compose up --build -d
```

Validar:

```powershell
.\scripts\simulate_player.ps1
```

Parar:

```powershell
docker compose down
```

Estado atual:
- Compose executa frontend, player, backend e PostgreSQL.
- Frontend fica disponivel em `http://127.0.0.1:8080`.
- Player fica disponivel em `http://127.0.0.1:8091`.
- Frontend encaminha `/api` e `/health` para o backend pela rede interna.
- Os quatro servicos possuem health check.
- Banco persiste em `runtime/postgres/data`.
- Sessoes demo ficam na tabela `device_sessions`.
- Manifestos demo ficam em memoria.

## Armazenamento Docker local

O Compose monta pastas do projeto dentro do container:

- `runtime/data` -> `/app/runtime/data`
- `runtime/media` -> `/app/runtime/media`
- `runtime/tmp` -> `/app/runtime/tmp`
- `logs` -> `/app/logs`
- `runtime/postgres/data` -> `/var/lib/postgresql/data`

Limite:
- Isso controla dados da aplicacao.
- Imagens, cache de build e volumes internos do Docker Desktop dependem da configuracao global do Docker.

## Rollback

- Manter versao anterior publicavel.
- Manter backup do banco antes de migracoes.
- Reverter deploy se health check falhar.
- Nao apagar midias durante deploy.

## Pontos pendentes

- Definir dominio.
- Configurar HTTPS.
- Definir storage definitivo de producao.
- Aprovar e executar o deploy PROD.
