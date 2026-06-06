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

Backup local automatizado:

```powershell
.\scripts\backup_stack.ps1
```

O script:
- Gera dump PostgreSQL no formato custom.
- Copia `runtime/media`.
- Cria `manifest.json` com SHA-256, tamanhos e quantidade de arquivos.
- Nao inclui `.env` ou segredos.

Teste de restore isolado:

```powershell
$backup = Get-ChildItem backups -Directory |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
.\scripts\test_restore.ps1 -BackupPath $backup.FullName
```

O teste cria banco temporario, restaura o dump, valida tabelas e remove o banco.

Regra:
- Criar pasta `backups/` fora do versionamento.
- Nunca commitar dump de banco.
- Validar restore em ambiente separado.
- Nunca executar restore destrutivo no banco operacional como teste.

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
