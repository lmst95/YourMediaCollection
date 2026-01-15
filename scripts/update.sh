#!/bin/bash
# Update script for YourMediaCollection
# Run this after pulling changes from Git

set -e

echo "=========================================="
echo "Your Media Collection - Update Script"
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

# Pull latest changes
print_info "Pulling latest changes from Git..."
git pull
print_success "Code updated"

# Install/update Python dependencies
print_info "Installing/updating Python dependencies..."
pip install -r requirements.txt --upgrade
print_success "Dependencies updated"

# Run new migrations
print_info "Running database migrations..."
python manage.py migrate
print_success "Migrations applied"

# Collect static files
print_info "Collecting static files..."
python manage.py collectstatic --noinput
print_success "Static files collected"

# Restart Docker services (if needed)
print_info "Restarting Docker services..."
docker-compose restart
print_success "Services restarted"

echo ""
echo "=========================================="
print_success "Update Complete!"
echo "=========================================="
echo ""
echo "Start the development server:"
echo "  python manage.py runserver"
echo ""
