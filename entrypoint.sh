#!/bin/sh
set -e

until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "Waiting for postgres..."
  sleep 1
done

python manage.py migrate --noinput
python manage.py seed_initial_data

exec "$@"
