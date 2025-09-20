docker compose: Dockerfile
	mkdir -p pyenv
	mkdir -p db
	docker compose build --build-arg UID=$(shell id -u)
	docker compose up -d postgres redis
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 15
	@echo "Starting web container..."
	docker compose up -d web
	@sleep 10
	@echo "Running setup script..."
	docker exec django-import-export-celery-web-1 /proj/setup-dev-env.sh
	@echo ""
	@echo "✅ Setup complete! You can now:"
	@echo "  ./develop.sh                                           # Enter development environment"
	@echo "  docker exec -it django-import-export-celery-web-1 bash # Manual container access"
	@echo "  docker compose up -d celery                           # Start celery worker"
	@echo ""
	@echo "🌐 Django admin will be available at: http://localhost:8001/admin/"
	@echo "👤 Login: admin / admin"

