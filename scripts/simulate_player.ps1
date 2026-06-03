param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$ActivationCode = "MOVI-DEMO-001",
    [string]$HardwareId = "BOX-SIM-001",
    [string]$PlayerVersion = "0.1.0"
)

$ErrorActionPreference = "Stop"

$health = Invoke-RestMethod -Uri "$BaseUrl/health"
$ready = Invoke-RestMethod -Uri "$BaseUrl/health/ready"

$activation = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/player/ativar" `
    -ContentType "application/json" `
    -Body (@{
        activation_code = $ActivationCode
        hardware_id = $HardwareId
        player_version = $PlayerVersion
    } | ConvertTo-Json -Compress)

$playlist = Invoke-RestMethod `
    -Uri "$BaseUrl/api/player/playlist" `
    -Headers @{ Authorization = "Bearer $($activation.token)" }

[pscustomobject]@{
    health = $health.status
    ready = $ready.status
    database = $ready.database
    device_id = $activation.device_id
    token_length = $activation.token.Length
    playlist_id = $playlist.playlist_id
    playlist_version = $playlist.version
    files = $playlist.files.Count
} | ConvertTo-Json -Compress
