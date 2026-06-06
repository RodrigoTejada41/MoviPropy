param(
    [ValidateSet("development", "production")]
    [string]$Environment = "development",
    [string]$HostName = "172.233.177.135",
    [string]$UserName = "moviprogy",
    [string]$IdentityFile = "$HOME\.ssh\moviprogy_vps_ed25519",
    [switch]$ApproveProduction
)

$ErrorActionPreference = "Stop"
if ($Environment -eq "production" -and -not $ApproveProduction) {
    throw "Deploy PROD bloqueado. Use -ApproveProduction somente apos homologacao e aprovacao."
}

$root = Split-Path -Parent $PSScriptRoot
$commit = (git -C $root rev-parse --short=12 HEAD).Trim()
$releaseName = "$(Get-Date -Format 'yyyyMMdd-HHmmss')-$commit"
$remoteRoot = if ($Environment -eq "development") {
    "/opt/moviprogy/dev"
} else {
    "/opt/moviprogy/prod"
}
$archive = Join-Path $env:TEMP "moviprogy-$releaseName.tar.gz"

try {
    git -C $root archive --format=tar.gz --output=$archive HEAD
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar pacote Git."
    }

    ssh -i $IdentityFile "$UserName@$HostName" `
        "mkdir -p '$remoteRoot/incoming' '$remoteRoot/releases/$releaseName'"
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao preparar diretorios remotos."
    }

    scp -i $IdentityFile $archive "${UserName}@${HostName}:$remoteRoot/incoming/$releaseName.tar.gz"
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao enviar release."
    }

    ssh -i $IdentityFile "$UserName@$HostName" `
        "tar -xzf '$remoteRoot/incoming/$releaseName.tar.gz' -C '$remoteRoot/releases/$releaseName' && chmod +x '$remoteRoot/releases/$releaseName/deploy/scripts/'*.sh && '$remoteRoot/releases/$releaseName/deploy/scripts/deploy.sh' '$Environment' '$remoteRoot/releases/$releaseName' && '$remoteRoot/releases/$releaseName/deploy/scripts/smoke_remote.sh' '$Environment' && rm -f '$remoteRoot/incoming/$releaseName.tar.gz'"
    if ($LASTEXITCODE -ne 0) {
        throw "Deploy ou smoke remoto falhou."
    }

    [pscustomobject]@{
        status = "ok"
        environment = $Environment
        release = $releaseName
        host = $HostName
    } | ConvertTo-Json -Compress
}
finally {
    Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
}
