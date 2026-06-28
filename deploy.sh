#!/bin/bash
set -e

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "=== Step 1: Starting backend services ==="
$COMPOSE up -d --build \
  postgres redis minio minio-init elasticsearch \
  backend celery_worker celery_beat flower \
  loki promtail grafana prometheus tempo \
  postgres-exporter redis-exporter elasticsearch-exporter node-exporter cadvisor certbot

echo "=== Waiting for backend to be healthy ==="
until $COMPOSE exec -T backend curl -sf http://localhost:8000/health > /dev/null 2>&1; do
  echo "  backend not ready yet, retrying in 5s..."
  sleep 5
done
echo "  backend is healthy!"

echo "=== Step 2: Building and starting frontend + nginx ==="
$COMPOSE up -d --build frontend nginx

echo "=== Deploy complete! ==="
echo "Site: https://sanjaranvarov.uz"
