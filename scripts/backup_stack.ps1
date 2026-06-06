param(
    [string]$OutputRoot = "backups",
    [string]$DatabaseContainer = "moviprogy-db",
    [string]$DatabaseName = "moviprogy",
    [string]$DatabaseUser = "moviprogy"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$outputBase = if ([System.IO.Path]::IsPathRooted($OutputRoot)) {
    $OutputRoot
} else {
    Join-Path $root $OutputRoot
}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $outputBase "moviprogy-$timestamp"
$databaseFile = Join-Path $backupDir "database.dump"
$mediaSource = Join-Path $root "runtime/media"
$mediaTarget = Join-Path $backupDir "media"
$containerDump = "/tmp/moviprogy-$timestamp.dump"

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

try {
    docker exec $DatabaseContainer pg_dump `
        -U $DatabaseUser `
        -d $DatabaseName `
        -Fc `
        -f $containerDump
    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump falhou."
    }

    docker cp "${DatabaseContainer}:${containerDump}" $databaseFile
    if ($LASTEXITCODE -ne 0) {
        throw "docker cp do dump falhou."
    }

    if (Test-Path -LiteralPath $mediaSource) {
        Copy-Item -LiteralPath $mediaSource -Destination $mediaTarget -Recurse
    } else {
        New-Item -ItemType Directory -Path $mediaTarget | Out-Null
    }

    $mediaFiles = @(Get-ChildItem -LiteralPath $mediaTarget -File -Recurse)
    $mediaBytes = ($mediaFiles | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $mediaBytes) {
        $mediaBytes = 0
    }
    $manifest = [ordered]@{
        created_at = (Get-Date).ToUniversalTime().ToString("o")
        database = @{
            name = $DatabaseName
            file = "database.dump"
            sha256 = (Get-FileHash -LiteralPath $databaseFile -Algorithm SHA256).Hash.ToLower()
            size_bytes = (Get-Item -LiteralPath $databaseFile).Length
        }
        media = @{
            directory = "media"
            files = $mediaFiles.Count
            size_bytes = $mediaBytes
        }
    }
    $manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backupDir "manifest.json") -Encoding UTF8
}
finally {
    docker exec $DatabaseContainer rm -f $containerDump 2>$null | Out-Null
}

[pscustomobject]@{
    status = "ok"
    backup = $backupDir
    database_bytes = (Get-Item -LiteralPath $databaseFile).Length
    media_files = @(Get-ChildItem -LiteralPath $mediaTarget -File -Recurse).Count
} | ConvertTo-Json -Compress
