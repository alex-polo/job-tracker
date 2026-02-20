#!/usr/bin/env bash

set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
fi

echo "Starting application..."
exec "$@"