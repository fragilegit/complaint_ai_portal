#!/bin/sh
set -e

until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  echo "Waiting for postgres..."
  sleep 1
done

exec "$@"
