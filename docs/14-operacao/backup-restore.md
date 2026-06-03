# Backup e Restore

## Objetivo

Definir como proteger e restaurar dados criticos.

## Dados criticos

- PostgreSQL.
- Midias em storage local.
- Configuracoes de ambiente.
- Logs de auditoria.
- Integracoes externas.

## Banco PostgreSQL

Backup local:

```powershell
docker exec moviprogy-db pg_dump -U moviprogy moviprogy > backups/moviprogy.sql
```

Restore local:

```powershell
Get-Content backups/moviprogy.sql | docker exec -i moviprogy-db psql -U moviprogy moviprogy
```

Regra:
- Criar pasta `backups/` fora do versionamento.
- Nunca commitar dump de banco.
- Validar restore em ambiente separado.

## Storage local

Backup:
- Copiar `runtime/media`.

Restore:
- Restaurar arquivos mantendo ids e caminhos esperados pelo banco.

Regra:
- Backup de banco e storage deve ser consistente.
- Nao restaurar banco de uma data e midias de outra sem validacao.

## Frequencia

Local:
- Manual antes de alteracoes destrutivas.

Homologacao:
- Diario.

Producao:
- Diario completo.
- Incremental quando volume justificar.
- Antes de toda migration.

## Retencao

Minimo recomendado:
- 7 diarios.
- 4 semanais.
- 6 mensais.

## Teste de restore

Periodicidade:
- Mensal em producao.
- Antes de release com migration critica.

Criterios:
- Banco sobe.
- API ready.
- Login funciona.
- Playlist e midias existem.
- Player consegue consultar manifesto.

