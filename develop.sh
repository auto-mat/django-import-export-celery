#!/bin/bash
docker compose down
docker compose up -d
echo "Waiting for services to start..."
sleep 10
echo "Entering development container..."
exec docker exec -u test -it django-import-export-celery-web-1 bash --init-file "/proj/dev-entrypoint.sh"
