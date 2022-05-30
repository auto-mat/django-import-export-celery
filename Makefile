docker-compose: Dockerfile
	mkdir -p pyenv
	mkdir -p db
	sudo docker-compose build --build-arg UID=$(shell id -u)
	sudo docker-compose up -d web postgres
	sudo docker exec -it django-import-export-celery_web_1 /proj/setup-dev-env.sh
	sudo docker-compose down

