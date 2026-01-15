# Deployment Guide - Your Media Collection

This guide explains how to set up the application on a deployment machine (not the development machine).

## Prerequisites

### Required Software
- **Git** - to clone the repository
- **Docker** & **Docker Compose** - for databases (PostgreSQL, Neo4j, Redis)
- **Python 3.11+** - for running Django
- **pip** - Python package manager

### Optional
- **Node.js 18+** - for frontend (Phase 2)

---

## Initial Setup (First Time)

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd YourMediaCollection
```

### 2. Run Setup Script

**Linux/macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows (PowerShell as Administrator):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup.ps1
```

This script will:
- Check Docker installation
- Create `.env` file from template
- Create necessary directories
- Start Docker services (PostgreSQL, Neo4j, Redis)
- Wait for services to be healthy

### 3. Configure Environment

Edit the `.env` file and set:

```bash
# Generate a new Django secret key (50+ random characters)
DJANGO_SECRET_KEY=your-super-secret-key-here-change-this

# Set strong passwords
POSTGRES_PASSWORD=your-postgres-password
NEO4J_PASSWORD=your-neo4j-password

# Get TMDb API key from https://www.themoviedb.org/settings/api
TMDB_API_KEY=your-tmdb-api-key

# Production settings
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

**Generate Django Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 5. Initialize Django

**Option A: Use script (Linux/macOS):**
```bash
chmod +x scripts/init_django.sh
./scripts/init_django.sh
```

**Option B: Manual steps:**
```bash
# Run migrations
python manage.py migrate

# Create superuser (interactive)
python manage.py createsuperuser

# Initialize Neo4j schema
python manage.py shell
>>> from core.services import get_neo4j_service
>>> neo4j = get_neo4j_service()
>>> neo4j.create_constraints()
>>> neo4j.create_indexes()
>>> neo4j.close()
>>> exit()

# Collect static files
python manage.py collectstatic --noinput
```

### 6. Verify Installation

```bash
# Check Django
python manage.py check

# Test Neo4j connection
python manage.py shell
>>> from core.services import get_neo4j_service
>>> neo4j = get_neo4j_service()
>>> neo4j.verify_connection()
True
>>> exit()

# Check Docker services
docker-compose ps
```

All services should show "Up" and "healthy".

---

## Running the Application

### Development Server

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Start Django development server
python manage.py runserver 0.0.0.0:8000
```

Access the application:
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/
- **Neo4j Browser**: http://localhost:7474/

### Background Tasks (Celery)

In separate terminal windows:

```bash
# Celery Worker
celery -A yourmedia worker -l info

# Celery Beat (scheduled tasks)
celery -A yourmedia beat -l info
```

---

## Updating the Application

When pulling new changes from Git:

**Linux/macOS:**
```bash
./scripts/update.sh
```

**Windows or Manual:**
```bash
# Pull changes
git pull

# Activate venv
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Docker services
docker-compose restart
```

---

## Data Management

### Initial Media Sync

Populate the database with media from external APIs:

```bash
# Sync movies and TV shows from TMDb (limit to 100 for testing)
python manage.py sync_tmdb --limit 100

# Sync books from Open Library
python manage.py sync_openlibrary --limit 100

# Sync music from MusicBrainz (slower, 1 req/sec)
python manage.py sync_musicbrainz --limit 50
```

For production, remove `--limit` to sync more data (will take longer).

### Backup Database

**PostgreSQL:**
```bash
docker-compose exec postgres pg_dump -U yourmedia_user yourmedia_db > backup_$(date +%Y%m%d).sql
```

**Restore:**
```bash
docker-compose exec -T postgres psql -U yourmedia_user yourmedia_db < backup_20240115.sql
```

**Neo4j:**
```bash
# Stop Neo4j
docker-compose stop neo4j

# Copy data directory
docker cp yourmedia_neo4j:/data ./neo4j_backup_$(date +%Y%m%d)

# Start Neo4j
docker-compose start neo4j
```

---

## Production Deployment

### Using Docker Compose (Backend Only)

Update `docker-compose.yml` to include backend service:

```yaml
backend:
  build:
    context: .
    dockerfile: Dockerfile.backend
  container_name: yourmedia_backend
  command: gunicorn yourmedia.wsgi:application --bind 0.0.0.0:8000 --workers 4
  volumes:
    - ./staticfiles:/app/staticfiles
    - ./media:/app/media
  env_file:
    - .env
  environment:
    DJANGO_SETTINGS_MODULE: yourmedia.settings.production
    DB_HOST: postgres
  ports:
    - "8000:8000"
  depends_on:
    - postgres
    - neo4j
    - redis
  networks:
    - yourmedia_network
```

Then:
```bash
docker-compose up -d --build
```

### Using Nginx (Reverse Proxy)

Install Nginx:
```bash
sudo apt-get install nginx  # Ubuntu/Debian
```

Create `/etc/nginx/sites-available/yourmedia`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/YourMediaCollection/staticfiles/;
    }

    location /media/ {
        alias /path/to/YourMediaCollection/media/;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/yourmedia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Systemd Service (Auto-start)

Create `/etc/systemd/system/yourmedia.service`:
```ini
[Unit]
Description=Your Media Collection Django App
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/YourMediaCollection
Environment="PATH=/path/to/YourMediaCollection/venv/bin"
ExecStart=/path/to/YourMediaCollection/venv/bin/gunicorn yourmedia.wsgi:application --bind 0.0.0.0:8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable yourmedia
sudo systemctl start yourmedia
sudo systemctl status yourmedia
```

---

## Troubleshooting

### Docker Services Not Starting

```bash
# Check logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis

# Restart services
docker-compose restart

# Full restart
docker-compose down
docker-compose up -d
```

### Database Connection Errors

Check `.env` file:
- Passwords match Docker Compose configuration
- Host is `localhost` for local dev, service name for Docker

### Neo4j Connection Failed

```bash
# Check Neo4j logs
docker-compose logs neo4j

# Access Neo4j browser
# http://localhost:7474/
# Username: neo4j
# Password: (from .env NEO4J_PASSWORD)
```

### Migrations Failed

```bash
# Reset migrations (WARNING: deletes data)
python manage.py migrate --fake-initial
python manage.py migrate
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in manage.py runserver
python manage.py runserver 0.0.0.0:8001
```

---

## Monitoring

### View Logs

```bash
# Django logs
tail -f logs/django.log

# Docker logs
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
```

### Database Status

```bash
# PostgreSQL
docker-compose exec postgres psql -U yourmedia_user -d yourmedia_db -c "SELECT COUNT(*) FROM media_catalog_media;"

# Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p yourpassword "MATCH (n) RETURN labels(n), count(n);"
```

---

## Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Set `DJANGO_DEBUG=False` in production
- [ ] Set proper `DJANGO_ALLOWED_HOSTS`
- [ ] Use HTTPS (SSL certificate)
- [ ] Restrict Neo4j browser access (port 7474)
- [ ] Restrict PostgreSQL access (port 5432)
- [ ] Set up firewall rules
- [ ] Regular backups
- [ ] Keep dependencies updated (`pip list --outdated`)

---

## Support

For issues or questions:
1. Check logs (Django, Docker, Neo4j)
2. Verify all services are running (`docker-compose ps`)
3. Review this deployment guide
4. Check README.md for API documentation

---

## Quick Reference

### Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View running services
docker-compose ps

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run tests
pytest

# Start Celery worker
celery -A yourmedia worker -l info
```

### Service URLs

- Django Admin: http://localhost:8000/admin/
- API Docs (Swagger): http://localhost:8000/api/docs/
- API Docs (ReDoc): http://localhost:8000/api/redoc/
- Neo4j Browser: http://localhost:7474/
- PostgreSQL: localhost:5432
- Redis: localhost:6379
