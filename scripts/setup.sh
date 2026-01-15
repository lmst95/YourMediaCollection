#!/bin/bash
# Setup script for YourMediaCollection
# Run this script on the deployment machine after cloning the repository

set -e  # Exit on error

echo "=========================================="
echo "Your Media Collection - Setup Script"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Docker is installed
print_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if Docker Compose is installed
print_info "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Create .env file if it doesn't exist
print_info "Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_info "⚠️  IMPORTANT: Edit .env file and set your passwords and API keys!"
    echo ""
    echo "Required changes in .env:"
    echo "  - DJANGO_SECRET_KEY (generate a new one)"
    echo "  - POSTGRES_PASSWORD (set a strong password)"
    echo "  - NEO4J_PASSWORD (set a strong password)"
    echo "  - TMDB_API_KEY (get from https://www.themoviedb.org/settings/api)"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
else
    print_success ".env file already exists"
fi

# Create necessary directories
print_info "Creating directories..."
mkdir -p logs static staticfiles media
print_success "Directories created"

# Start Docker services
print_info "Starting Docker services (PostgreSQL, Neo4j, Redis)..."
docker-compose up -d postgres neo4j redis
print_success "Docker services started"

# Wait for services to be healthy
print_info "Waiting for services to be ready (this may take 30-60 seconds)..."
sleep 10

# Check PostgreSQL health
print_info "Checking PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U yourmedia_user &> /dev/null; do
    echo -n "."
    sleep 2
done
print_success "PostgreSQL is ready"

# Check Neo4j health
print_info "Checking Neo4j..."
sleep 5  # Neo4j takes a bit longer to start
print_success "Neo4j should be ready"

# Check Redis health
print_info "Checking Redis..."
until docker-compose exec -T redis redis-cli ping &> /dev/null; do
    echo -n "."
    sleep 2
done
print_success "Redis is ready"

echo ""
echo "=========================================="
print_success "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Install Python dependencies (if running locally):"
echo "     python -m venv venv"
echo "     source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "     pip install -r requirements.txt"
echo ""
echo "  2. Run database migrations:"
echo "     python manage.py migrate"
echo ""
echo "  3. Create superuser:"
echo "     python manage.py createsuperuser"
echo ""
echo "  4. Create Neo4j constraints:"
echo "     python manage.py shell"
echo "     >>> from core.services import get_neo4j_service"
echo "     >>> neo4j = get_neo4j_service()"
echo "     >>> neo4j.create_constraints()"
echo "     >>> neo4j.create_indexes()"
echo ""
echo "  5. Sync initial media data (optional):"
echo "     python manage.py sync_tmdb --limit 100"
echo "     python manage.py sync_openlibrary --limit 100"
echo ""
echo "  6. Start development server:"
echo "     python manage.py runserver"
echo ""
echo "Access points:"
echo "  - Django Admin: http://localhost:8000/admin/"
echo "  - API Docs: http://localhost:8000/api/docs/"
echo "  - Neo4j Browser: http://localhost:7474/"
echo "  - PostgreSQL: localhost:5432"
echo ""
