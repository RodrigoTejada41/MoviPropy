# Manual Operacional

## Objetivo

Orientar manutencao tecnica do sistema.

## Subir ambiente local

```powershell
docker compose up --build -d
```

## Parar ambiente

```powershell
docker compose down
```

## Testes

```powershell
python -m pytest
```

Com PostgreSQL:

```powershell
$env:DATABASE_URL='postgresql://moviprogy:moviprogy_dev_password@127.0.0.1:5432/moviprogy'
python -m pytest
```

## Health

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/health/ready
```

## Login admin local

```powershell
$login = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/auth/login" `
  -ContentType "application/json" `
  -Body '{"email":"admin@moviprogy.local","senha":"moviprogy_admin_dev_password"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }
```

## Simular player

```powershell
.\scripts\simulate_player.ps1
```

## Ver containers

```powershell
docker compose ps
```

## Logs

```powershell
docker compose logs moviprogy-api
docker compose logs moviprogy-db
```

## Problemas comuns

Docker daemon parado:
```powershell
Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
```

Banco unhealthy:
- Aguardar bootstrap inicial.
- Verificar `runtime/postgres/data`.
- Ver logs do container.

Testes travando em Temp:
- Manter `pytest.ini` com `--basetemp=.pytest_tmp`.

## Antes de alterar codigo

Ler:
- `AGENTS.md`.
- `PROJECT_RESUME.md`.
- `LESSONS_LEARNED.md`.
- `KNOWLEDGE_BASE.md`.
- `ARCHITECTURE_DECISIONS.md`.

## Antes de commit

Verificar:
- Testes passaram.
- Docs atualizadas.
- Sem dados sensiveis.
- Sem runtime/logs versionados.
- Sem violar ADRs.

