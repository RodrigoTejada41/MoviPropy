param(
    [string]$BaseUrl = "http://127.0.0.1:8080",
    [string]$PlayerUrl = "http://127.0.0.1:8091",
    [string]$Email = $env:MOVIPROGY_ADMIN_EMAIL,
    [string]$Password = $env:MOVIPROGY_ADMIN_PASSWORD
)

$ErrorActionPreference = "Stop"

if (-not $Email -or -not $Password) {
    throw "Informe -Email e -Password ou configure MOVIPROGY_ADMIN_EMAIL e MOVIPROGY_ADMIN_PASSWORD."
}

$ui = Invoke-WebRequest -Uri $BaseUrl -UseBasicParsing
$uiHealth = Invoke-WebRequest -Uri "$BaseUrl/health-ui" -UseBasicParsing
$player = Invoke-WebRequest -Uri $PlayerUrl -UseBasicParsing
$playerHealth = Invoke-WebRequest -Uri "$PlayerUrl/health-player" -UseBasicParsing
$health = Invoke-RestMethod -Uri "$BaseUrl/health"
$ready = Invoke-RestMethod -Uri "$BaseUrl/health/ready"

$login = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/auth/login" `
    -ContentType "application/json" `
    -Body (@{
        email = $Email
        senha = $Password
    } | ConvertTo-Json -Compress)

$headers = @{ Authorization = "Bearer $($login.access_token)" }
$clientes = Invoke-RestMethod `
    -Uri "$BaseUrl/api/admin/clientes?limit=1&offset=0" `
    -Headers $headers

$logout = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/auth/logout" `
    -Headers $headers

$result = [pscustomobject]@{
    frontend = $ui.StatusCode -eq 200 -and $ui.Content -match '<div id="root"></div>'
    frontend_health = $uiHealth.StatusCode -eq 200
    player = $player.StatusCode -eq 200 -and $player.Content -match '<div id="root"></div>'
    player_health = $playerHealth.StatusCode -eq 200
    api_health = $health.status
    database = $ready.database
    login = $login.usuario.email -eq $Email
    protected_route = $clientes.total -ge 0
    logout = $logout.status
}

if (
    -not $result.frontend -or
    -not $result.frontend_health -or
    -not $result.player -or
    -not $result.player_health -or
    $result.api_health -ne "ok" -or
    $result.database -ne "available" -or
    -not $result.login -or
    -not $result.protected_route -or
    $result.logout -ne "logout efetuado"
) {
    throw "Smoke test falhou: $($result | ConvertTo-Json -Compress)"
}

$result | ConvertTo-Json -Compress
