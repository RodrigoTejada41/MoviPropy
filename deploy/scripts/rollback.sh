#!/usr/bin/env bash
set -euo pipefail

environment="${1:?uso: rollback.sh <development|production>}"

case "$environment" in
  development) environment_root="/opt/moviprogy/dev" ;;
  production) environment_root="/opt/moviprogy/prod" ;;
  *) echo "Ambiente invalido: $environment" >&2; exit 2 ;;
esac

test -L "$environment_root/previous"
previous_release="$(readlink -f "$environment_root/previous")"
exec "$previous_release/deploy/scripts/deploy.sh" "$environment" "$previous_release"
