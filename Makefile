docker compose: Dockerfile
	mkdir -p pyenv
	mkdir -p db
	docker compose build --build-arg UID=$(shell id -u)
	docker compose up -d postgres redis
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 10
	@echo "Starting web and celery containers..."
	docker compose up -d web celery
	@sleep 10
	@echo "Running setup script..."
	docker exec django-import-export-celery-web-1 /proj/setup-dev-env.sh
	@echo ""
	@echo "✅ Setup complete! Django server and Celery worker are running automatically."
	@echo ""
	@echo "🌐 Django admin is available at: http://localhost:8000/admin/"
	@echo ""
	@echo "Optional commands:"
	@echo "  ./develop.sh                                          # Enter development environment"
	@echo "  docker exec -it django-import-export-celery-web-1 bash # Manual container access"
	@echo "  docker compose logs celery                            # View celery logs"
	@echo "👤 Login: admin / admin"

