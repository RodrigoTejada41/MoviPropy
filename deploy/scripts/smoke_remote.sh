#!/usr/bin/env bash
set -euo pipefail

environment="${1:?uso: smoke_remote.sh <development|production>}"

case "$environment" in
  development)
    base_url="http://127.0.0.1:8081"
    player_url="http://127.0.0.1:8092"
    env_file="/opt/moviprogy/dev/shared/.env"
    ;;
  production)
    base_url="${PRODUCTION_BASE_URL:?PRODUCTION_BASE_URL obrigatorio}"
    player_url="${PRODUCTION_PLAYER_URL:?PRODUCTION_PLAYER_URL obrigatorio}"
    env_file="/opt/moviprogy/prod/shared/.env"
    ;;
  *)
    echo "Ambiente invalido: $environment" >&2
    exit 2
    ;;
esac

set -a
source "$env_file"
set +a

curl --fail --silent --show-error "$base_url/health-ui" >/dev/null
curl --fail --silent --show-error "$base_url/health/ready" | grep -q '"database":"available"'
curl --fail --silent --show-error "$player_url/health-player" >/dev/null

token="$(
  curl --fail --silent --show-error \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$MOVIPROGY_ADMIN_EMAIL\",\"senha\":\"$MOVIPROGY_ADMIN_PASSWORD\"}" \
    "$base_url/api/auth/login" |
  python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])'
)"

curl --fail --silent --show-error \
  -H "Authorization: Bearer $token" \
  "$base_url/api/admin/clientes?limit=1" >/dev/null

curl --fail --silent --show-error \
  -X POST \
  -H "Authorization: Bearer $token" \
  "$base_url/api/auth/logout" >/dev/null
