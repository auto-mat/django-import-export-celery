#!/bin/bash
docker-compose down
docker-compose up -d
exec docker exec -u test -it django-import-export-celery_web_1 bash --init-file "/proj/dev-entrypoint.sh"
