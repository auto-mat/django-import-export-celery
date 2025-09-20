#!/bin/bash
set -e

echo "Setting up development environment..."

# Install the package in development mode
pip install -e .

# Install additional dependencies
pip install -r requirements_test.txt

# Install redis client
pip install redis

cd example

# Set database host to postgres when running in Docker
export DATABASE_HOST=postgres

echo "Running Django migrations..."
python manage.py migrate

echo "Creating superuser..."
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell

echo "Development environment setup complete!"
echo "You can now run: python manage.py runserver 0.0.0.0:8000"
