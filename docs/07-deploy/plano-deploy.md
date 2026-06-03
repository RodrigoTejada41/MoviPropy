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

Limite atual:
- Compose executa backend e PostgreSQL.
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

- Definir provedor.
- Definir dominio.
- Definir estrategia de storage.
- Definir CI/CD.
