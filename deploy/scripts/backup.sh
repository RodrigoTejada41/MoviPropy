#!/usr/bin/env bash
set -euo pipefail

environment="${1:?uso: backup.sh <development|production>}"

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
test -f "$env_file"
set -a
source "$env_file"
set +a

timestamp="$(date -u +%Y%m%d-%H%M%S)"
backup_dir="${BACKUP_ROOT:?BACKUP_ROOT obrigatorio}/moviprogy-$timestamp"
mkdir -p "$backup_dir/media"

db_container="$(docker compose \
  --project-name "$project_name" \
  --env-file "$env_file" \
  --file "$environment_root/current/deploy/compose.yml" \
  ps -q moviprogy-db)"
test -n "$db_container"

docker exec "$db_container" pg_dump \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  -Fc > "$backup_dir/database.dump"

if [[ -d "$DATA_ROOT/media" ]]; then
  cp -a "$DATA_ROOT/media/." "$backup_dir/media/"
fi

sha256sum "$backup_dir/database.dump" > "$backup_dir/database.dump.sha256"

find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d \
  -mtime +30 -exec rm -rf {} +

echo "$backup_dir"
