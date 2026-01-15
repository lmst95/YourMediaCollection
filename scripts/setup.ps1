# Setup script for YourMediaCollection (Windows PowerShell)
# Run this script on the deployment machine after cloning the repository

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Your Media Collection - Setup Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Print-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Info {
    param($Message)
    Write-Host "→ $Message" -ForegroundColor Yellow
}

function Print-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Check if Docker is installed
Print-Info "Checking Docker installation..."
try {
    docker --version | Out-Null
    Print-Success "Docker is installed"
} catch {
    Print-Error "Docker is not installed. Please install Docker Desktop first."
    exit 1
}

# Check if Docker Compose is installed
Print-Info "Checking Docker Compose installation..."
try {
    docker-compose --version | Out-Null
    Print-Success "Docker Compose is installed"
} catch {
    Print-Error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}

# Create .env file if it doesn't exist
Print-Info "Setting up environment file..."
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Print-Success "Created .env file from template"
    Print-Info "⚠️  IMPORTANT: Edit .env file and set your passwords and API keys!"
    Write-Host ""
    Write-Host "Required changes in .env:"
    Write-Host "  - DJANGO_SECRET_KEY (generate a new one)"
    Write-Host "  - POSTGRES_PASSWORD (set a strong password)"
    Write-Host "  - NEO4J_PASSWORD (set a strong password)"
    Write-Host "  - TMDB_API_KEY (get from https://www.themoviedb.org/settings/api)"
    Write-Host ""
    Read-Host "Press Enter after you've updated the .env file"
} else {
    Print-Success ".env file already exists"
}

# Create necessary directories
Print-Info "Creating directories..."
New-Item -ItemType Directory -Force -Path logs, static, staticfiles, media | Out-Null
Print-Success "Directories created"

# Start Docker services
Print-Info "Starting Docker services (PostgreSQL, Neo4j, Redis)..."
docker-compose up -d postgres neo4j redis
Print-Success "Docker services started"

# Wait for services to be ready
Print-Info "Waiting for services to be ready (this may take 30-60 seconds)..."
Start-Sleep -Seconds 10

# Check PostgreSQL health
Print-Info "Checking PostgreSQL..."
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        docker-compose exec -T postgres pg_isready -U yourmedia_user 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            break
        }
    } catch {}
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
    $attempt++
}
Print-Success "PostgreSQL is ready"

# Check Neo4j health
Print-Info "Checking Neo4j..."
Start-Sleep -Seconds 5
Print-Success "Neo4j should be ready"

# Check Redis health
Print-Info "Checking Redis..."
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        docker-compose exec -T redis redis-cli ping 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            break
        }
    } catch {}
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
    $attempt++
}
Print-Success "Redis is ready"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Print-Success "Setup Complete!"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Install Python dependencies (if running locally):"
Write-Host "     python -m venv venv"
Write-Host "     venv\Scripts\activate"
Write-Host "     pip install -r requirements.txt"
Write-Host ""
Write-Host "  2. Run database migrations:"
Write-Host "     python manage.py migrate"
Write-Host ""
Write-Host "  3. Create superuser:"
Write-Host "     python manage.py createsuperuser"
Write-Host ""
Write-Host "  4. Create Neo4j constraints:"
Write-Host "     python manage.py shell"
Write-Host "     >>> from core.services import get_neo4j_service"
Write-Host "     >>> neo4j = get_neo4j_service()"
Write-Host "     >>> neo4j.create_constraints()"
Write-Host "     >>> neo4j.create_indexes()"
Write-Host ""
Write-Host "  5. Sync initial media data (optional):"
Write-Host "     python manage.py sync_tmdb --limit 100"
Write-Host "     python manage.py sync_openlibrary --limit 100"
Write-Host ""
Write-Host "  6. Start development server:"
Write-Host "     python manage.py runserver"
Write-Host ""
Write-Host "Access points:"
Write-Host "  - Django Admin: http://localhost:8000/admin/"
Write-Host "  - API Docs: http://localhost:8000/api/docs/"
Write-Host "  - Neo4j Browser: http://localhost:7474/"
Write-Host "  - PostgreSQL: localhost:5432"
Write-Host ""
