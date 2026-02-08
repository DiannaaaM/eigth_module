#!/usr/bin/env bash
set -euo pipefail

cd /app

# Ensure directories exist before collectstatic/migrations run.
mkdir -p staticfiles media

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi

exec "$@"

