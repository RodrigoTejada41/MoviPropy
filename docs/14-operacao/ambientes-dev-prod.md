# Ambientes DEV e PROD

## Fluxo obrigatorio

```text
feature/* ou bugfix/*
        |
        v
develop -> CI -> deploy automatico DEV -> homologacao
        |
        v
main -> tag de release -> aprovacao -> deploy manual PROD
```

## Isolamento

| Recurso | DEV | PROD |
|---|---|---|
| Branch | `develop` | `main` |
| Compose project | `moviprogy-dev` | `moviprogy-prod` |
| Banco | `moviprogy_dev` | `moviprogy_prod` |
| Dados | `/opt/moviprogy/dev/data` | `/opt/moviprogy/prod/data` |
| Logs | `/opt/moviprogy/dev/logs` | `/opt/moviprogy/prod/logs` |
| Backups | `/opt/moviprogy/dev/backups` | `/opt/moviprogy/prod/backups` |
| Configuracao | `/opt/moviprogy/dev/shared/.env` | `/opt/moviprogy/prod/shared/.env` |
| Painel | porta `8081` | dominio HTTPS |
| Player | porta `8092` | dominio HTTPS separado |

Credenciais, tokens, banco, storage e integracoes nao podem ser compartilhados.

## Deploy DEV

- Trigger: push aprovado em `develop`.
- Workflow: `.github/workflows/ci.yml`.
- Requisitos: testes backend, frontend e player aprovados.
- O workflow empacota apenas arquivos rastreados pelo Git.
- Smoke remoto valida health, banco, login, rota protegida, logout e player.

Deploy manual emergencial:

```powershell
.\scripts\deploy_vps.ps1 -Environment development
```

## Deploy PROD

- Trigger manual em `.github/workflows/deploy-production.yml`.
- Permitido somente a partir de `main`.
- Exige tag de release existente em `main`.
- Exige confirmacao `PUBLICAR-PRODUCAO`.
- Exige aprovacao do ambiente `production` no GitHub.
- Exige `PRODUCTION_APPROVED=true` no arquivo secreto do servidor.
- Exige dominio e HTTPS configurados.
- Executa backup antes de substituir uma release existente.

Producao permanece bloqueada enquanto dominio, certificados e aprovacao nao existirem.

## Rollback

```bash
/opt/moviprogy/dev/current/deploy/scripts/rollback.sh development
/opt/moviprogy/prod/current/deploy/scripts/rollback.sh production
```

## Segredos GitHub

Ambiente `development`:

- `DEV_HOST`
- `DEV_USER`
- `DEV_SSH_PRIVATE_KEY`

Ambiente `production`:

- `PROD_HOST`
- `PROD_USER`
- `PROD_SSH_PRIVATE_KEY`
- `PRODUCTION_BASE_URL`
- `PRODUCTION_PLAYER_URL`

## Restricao de capacidade

A VPS atual possui aproximadamente 1 GB de RAM. DEV pode operar com limites de memoria e build serial. DEV e PROD simultaneos nao devem ser considerados seguros nessa capacidade. Antes de ativar PROD, ampliar para no minimo 2 GB de RAM; 4 GB e recomendado para margem operacional e builds.
