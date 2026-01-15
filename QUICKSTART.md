# Quick Start Guide

Get **Your Media Collection** up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd YourMediaCollection
```

### 2. Run Setup Script

**Linux/macOS:**
```bash
./scripts/setup.sh
```

**Windows:**
```powershell
.\scripts\setup.ps1
```

This will:
- ✓ Check Docker installation
- ✓ Create `.env` file
- ✓ Start PostgreSQL, Neo4j, Redis

### 3. Edit Configuration

Open `.env` and update:

```bash
# Required: Change these!
DJANGO_SECRET_KEY=your-secret-key-here
POSTGRES_PASSWORD=your-password
NEO4J_PASSWORD=your-password

# Optional: Add TMDb API key for movie/TV data
TMDB_API_KEY=your-tmdb-key
```

Generate secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Setup Python

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
# Create database tables
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Initialize Neo4j
python manage.py shell
>>> from core.services import get_neo4j_service
>>> neo4j = get_neo4j_service()
>>> neo4j.create_constraints()
>>> neo4j.create_indexes()
>>> exit()
```

### 6. Start Application

```bash
python manage.py runserver
```

**Access:**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/

## Using Makefile (Optional)

If you have `make` installed:

```bash
# Setup
make setup
make install

# Start services
make start

# Run migrations
make migrate

# Create superuser
make superuser

# Start server
make runserver
```

## What's Next?

1. **Sync Media Data** (optional):
   ```bash
   python manage.py sync_tmdb --limit 100
   python manage.py sync_openlibrary --limit 100
   ```

2. **Explore API**: Visit http://localhost:8000/api/docs/

3. **Read Full Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

## Troubleshooting

### Docker not starting?
```bash
docker-compose logs
docker-compose restart
```

### Port already in use?
```bash
# Change port in command
python manage.py runserver 8001
```

### Need help?
Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting

## Quick Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Django shell
python manage.py shell

# Run tests
pytest

# Format code
black .
```

---

**That's it!** You're ready to start using Your Media Collection. 🎉
