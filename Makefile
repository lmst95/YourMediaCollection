# Makefile for Your Media Collection

.PHONY: help setup start stop restart migrate makemigrations superuser shell test clean

help:
	@echo "Your Media Collection - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup         - Run initial setup (Docker + Python)"
	@echo "  make install       - Install Python dependencies"
	@echo ""
	@echo "Docker Services:"
	@echo "  make start         - Start Docker services"
	@echo "  make stop          - Stop Docker services"
	@echo "  make restart       - Restart Docker services"
	@echo "  make logs          - View Docker logs"
	@echo ""
	@echo "Django:"
	@echo "  make migrate       - Run database migrations"
	@echo "  make makemigrations- Create new migrations"
	@echo "  make superuser     - Create Django superuser"
	@echo "  make shell         - Open Django shell"
	@echo "  make runserver     - Start Django development server"
	@echo ""
	@echo "Development:"
	@echo "  make test          - Run tests"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Run flake8 linter"
	@echo "  make clean         - Clean temporary files"
	@echo ""

# Setup
setup:
	@echo "Running setup script..."
	@./scripts/setup.sh

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Docker
start:
	@echo "Starting Docker services..."
	docker-compose up -d

stop:
	@echo "Stopping Docker services..."
	docker-compose down

restart:
	@echo "Restarting Docker services..."
	docker-compose restart

logs:
	@echo "Viewing Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f

# Django
migrate:
	@echo "Running migrations..."
	python manage.py migrate

makemigrations:
	@echo "Creating migrations..."
	python manage.py makemigrations

superuser:
	@echo "Creating superuser..."
	python manage.py createsuperuser

shell:
	@echo "Opening Django shell..."
	python manage.py shell

runserver:
	@echo "Starting Django development server..."
	python manage.py runserver 0.0.0.0:8000

collectstatic:
	@echo "Collecting static files..."
	python manage.py collectstatic --noinput

# Development
test:
	@echo "Running tests..."
	pytest

format:
	@echo "Formatting code with black..."
	black .

lint:
	@echo "Running flake8..."
	flake8 .

clean:
	@echo "Cleaning temporary files..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	@echo "Clean complete!"

# Database
db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	docker-compose up -d postgres neo4j redis
	@echo "Waiting for services..."
	sleep 10
	python manage.py migrate
	@echo "Database reset complete!"

# Celery
celery-worker:
	@echo "Starting Celery worker..."
	celery -A yourmedia worker -l info

celery-beat:
	@echo "Starting Celery beat..."
	celery -A yourmedia beat -l info

# Neo4j
neo4j-shell:
	@echo "Opening Neo4j Cypher shell..."
	docker-compose exec neo4j cypher-shell -u neo4j

neo4j-init:
	@echo "Initializing Neo4j schema..."
	python manage.py shell -c "from core.services import get_neo4j_service; neo4j = get_neo4j_service(); neo4j.create_constraints(); neo4j.create_indexes(); print('Neo4j initialized')"

# Data Sync
sync-tmdb:
	@echo "Syncing TMDb data (limit 100)..."
	python manage.py sync_tmdb --limit 100

sync-books:
	@echo "Syncing OpenLibrary data (limit 100)..."
	python manage.py sync_openlibrary --limit 100

sync-music:
	@echo "Syncing MusicBrainz data (limit 50)..."
	python manage.py sync_musicbrainz --limit 50

sync-all:
	@echo "Syncing all data sources..."
	make sync-tmdb
	make sync-books
	make sync-music
