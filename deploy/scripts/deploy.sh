#!/usr/bin/env bash
set -euo pipefail
export COMPOSE_PARALLEL_LIMIT=1

environment="${1:?uso: deploy.sh <development|production> <release_dir>}"
release_dir="${2:?release_dir obrigatorio}"

case "$environment" in
  development)
    environment_root="/opt/moviprogy/dev"
    project_name="moviprogy-dev"
    ;;
  production)
    environment_root="/opt/moviprogy/prod"
    project_name="moviprogy-prod"
    ;;
  *)
    echo "Ambiente invalido: $environment" >&2
    exit 2
    ;;
esac

env_file="$environment_root/shared/.env"
compose_file="$release_dir/deploy/compose.yml"

test -f "$env_file"
test -f "$compose_file"

set -a
source "$env_file"
set +a

if [[ "$environment" == "production" ]]; then
  if [[ "${PRODUCTION_APPROVED:-false}" != "true" ]]; then
    echo "Deploy PROD bloqueado: PRODUCTION_APPROVED deve ser true." >&2
    exit 3
  fi
  if [[ "${MOVIPROGY_ALLOWED_HOSTS:-}" == *"SEU_DOMINIO_PROD"* ]] ||
    [[ "${MOVIPROGY_GOOGLE_REDIRECT_URI:-}" == *"SEU_DOMINIO_PROD"* ]]; then
    echo "Deploy PROD bloqueado: dominio de producao nao configurado." >&2
    exit 3
  fi
fi

mkdir -p \
  "$environment_root/data/postgres" \
  "$environment_root/data/data" \
  "$environment_root/data/media" \
  "$environment_root/data/tmp" \
  "$environment_root/logs/api" \
  "$environment_root/backups" \
  "$environment_root/releases"

if [[ "$environment" == "production" && -L "$environment_root/current" ]]; then
  "$release_dir/deploy/scripts/backup.sh" production
fi

docker compose \
  --project-name "$project_name" \
  --env-file "$env_file" \
  --file "$compose_file" \
  config --quiet

docker compose \
  --project-name "$project_name" \
  --env-file "$env_file" \
  --file "$compose_file" \
  up --build --detach --remove-orphans

for attempt in $(seq 1 30); do
  frontend_container="$(docker compose \
    --project-name "$project_name" \
    --env-file "$env_file" \
    --file "$compose_file" \
    ps -q moviprogy-frontend)"
  if [[ -n "$frontend_container" ]] &&
    [[ "$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$frontend_container")" == "healthy" ]]; then
    break
  fi
  if [[ "$attempt" == "30" ]]; then
    docker compose \
      --project-name "$project_name" \
      --env-file "$env_file" \
      --file "$compose_file" \
      ps
    exit 1
  fi
  sleep 5
done

previous_release=""
if [[ -L "$environment_root/current" ]]; then
  previous_release="$(readlink -f "$environment_root/current")"
fi
ln -sfn "$release_dir" "$environment_root/current"
if [[ -n "$previous_release" ]]; then
  ln -sfn "$previous_release" "$environment_root/previous"
fi

find "$environment_root/releases" -mindepth 1 -maxdepth 1 -type d \
  -printf '%T@ %p\n' | sort -nr | tail -n +6 | cut -d' ' -f2- | xargs -r rm -rf

docker image prune -f >/dev/null
