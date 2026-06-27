#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Running seed..."
python scripts/seeds/seed_catalog.py

echo "Starting server..."
exec uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --no-access-log
