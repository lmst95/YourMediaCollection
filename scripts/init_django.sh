#!/bin/bash
# Django initialization script
# Run this after setup.sh and installing Python dependencies

set -e

echo "=========================================="
echo "Django Initialization"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Run migrations
print_info "Running database migrations..."
python manage.py migrate
print_success "Migrations completed"

# Create superuser (interactive)
print_info "Creating superuser..."
python manage.py createsuperuser
print_success "Superuser created"

# Initialize Neo4j schema
print_info "Setting up Neo4j schema (constraints and indexes)..."
python manage.py shell <<EOF
from core.services import get_neo4j_service
neo4j = get_neo4j_service()
neo4j.create_constraints()
neo4j.create_indexes()
neo4j.close()
print("Neo4j schema initialized")
EOF
print_success "Neo4j schema ready"

# Collect static files
print_info "Collecting static files..."
python manage.py collectstatic --noinput
print_success "Static files collected"

echo ""
echo "=========================================="
print_success "Django Initialization Complete!"
echo "=========================================="
echo ""
echo "You can now:"
echo "  - Start the development server: python manage.py runserver"
echo "  - Access Django Admin: http://localhost:8000/admin/"
echo "  - Access API Docs: http://localhost:8000/api/docs/"
echo ""
echo "Optional: Sync initial media data"
echo "  python manage.py sync_tmdb --limit 100"
echo "  python manage.py sync_openlibrary --limit 100"
echo "  python manage.py sync_musicbrainz --limit 50"
echo ""
