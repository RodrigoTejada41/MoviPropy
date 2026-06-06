param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [string]$DatabaseContainer = "moviprogy-db",
    [string]$DatabaseUser = "moviprogy"
)

$ErrorActionPreference = "Stop"
$resolvedBackup = (Resolve-Path -LiteralPath $BackupPath).Path
$manifestPath = Join-Path $resolvedBackup "manifest.json"
$databaseFile = Join-Path $resolvedBackup "database.dump"

if (-not (Test-Path -LiteralPath $manifestPath) -or -not (Test-Path -LiteralPath $databaseFile)) {
    throw "Backup incompleto."
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$actualHash = (Get-FileHash -LiteralPath $databaseFile -Algorithm SHA256).Hash.ToLower()
if ($actualHash -ne $manifest.database.sha256) {
    throw "Checksum do dump invalido."
}

$suffix = [Guid]::NewGuid().ToString("N").Substring(0, 8)
$testDatabase = "moviprogy_restore_$suffix"
$containerDump = "/tmp/$testDatabase.dump"

try {
    docker cp $databaseFile "${DatabaseContainer}:${containerDump}"
    if ($LASTEXITCODE -ne 0) {
        throw "docker cp do dump falhou."
    }

    docker exec $DatabaseContainer createdb -U $DatabaseUser $testDatabase
    if ($LASTEXITCODE -ne 0) {
        throw "Criacao do banco temporario falhou."
    }

    docker exec $DatabaseContainer pg_restore `
        -U $DatabaseUser `
        -d $testDatabase `
        --no-owner `
        --no-privileges `
        $containerDump
    if ($LASTEXITCODE -ne 0) {
        throw "Restore do banco temporario falhou."
    }

    $tableCount = docker exec $DatabaseContainer psql `
        -U $DatabaseUser `
        -d $testDatabase `
        -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
    if ($LASTEXITCODE -ne 0 -or [int]$tableCount -lt 1) {
        throw "Banco restaurado sem tabelas."
    }

    [pscustomobject]@{
        status = "ok"
        database = $testDatabase
        tables = [int]$tableCount
    } | ConvertTo-Json -Compress
}
finally {
    docker exec $DatabaseContainer dropdb -U $DatabaseUser --if-exists $testDatabase 2>$null | Out-Null
    docker exec $DatabaseContainer rm -f $containerDump 2>$null | Out-Null
}
