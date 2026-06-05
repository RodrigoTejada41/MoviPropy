param(
    [string]$ClientId = "",
    [string]$ClientSecret = "",
    [string]$RedirectUri = "http://127.0.0.1:8000/api/integrations/google-drive/callback",
    [switch]$Simulated
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $root ".env"

function New-TokenKey {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($bytes)
    }
    finally {
        $rng.Dispose()
    }
    return [Convert]::ToBase64String($bytes).Substring(0, 32)
}

if (-not $Simulated -and (-not $ClientId -or -not $ClientSecret)) {
    throw "Informe -ClientId e -ClientSecret ou use -Simulated para teste local."
}

$lines = @(
    "POSTGRES_DB=moviprogy",
    "POSTGRES_USER=moviprogy",
    "POSTGRES_PASSWORD=moviprogy_dev_password",
    "ADMIN_API_TOKEN=moviprogy_admin_dev_token",
    "MOVIPROGY_ADMIN_EMAIL=admin@moviprogy.local",
    "MOVIPROGY_ADMIN_PASSWORD=moviprogy_admin_dev_password",
    "MOVIPROGY_MAX_UPLOAD_BYTES=536870912",
    "MOVIPROGY_GOOGLE_CLIENT_ID=$ClientId",
    "MOVIPROGY_GOOGLE_CLIENT_SECRET=$ClientSecret",
    "MOVIPROGY_GOOGLE_REDIRECT_URI=$RedirectUri",
    "MOVIPROGY_GOOGLE_TOKEN_KEY=$(New-TokenKey)",
    "MOVIPROGY_GOOGLE_OAUTH_SIMULATED=$($Simulated.IsPresent.ToString().ToLower())",
    "MOVIPROGY_GOOGLE_SIMULATED_EMAIL=simulado@moviprogy.local"
)

Set-Content -LiteralPath $envPath -Value $lines -Encoding UTF8
Write-Host "Arquivo .env configurado em $envPath"
Write-Host "Execute: docker compose up --build -d"
