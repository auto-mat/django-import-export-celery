#!/bin/bash
echo "Starting database and redis services..."
docker compose up -d postgres redis
echo "Waiting for services to start..."
sleep 5
echo "Entering development container (without auto-starting web server)..."
exec docker run --rm -it \
  --network django-import-export-celery_default \
  -v ./:/proj/ \
  -v ./pyenv:/home/test \
  -w /proj/ \
  -u test \
  -e DATABASE_HOST=postgres \
  django-import-export-celery-web bash --init-file "/proj/dev-entrypoint.sh"
