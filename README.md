# Your Media Collection

A personal media collection management system with social features. Track movies, TV shows, books, music, concerts, and documents you own, have watched/read, or wish to experience.

## Architecture

- **Backend**: Django + Django REST Framework
- **Databases**:
  - PostgreSQL (structured data, source of truth)
  - Neo4j (relationship graph for recommendations)
- **Task Queue**: Celery + Redis
- **Frontend**: React + TypeScript + Vite (coming soon)

## Features (Phase 1)

- Personal media collection management
- Pre-populated catalog from open-source APIs:
  - TMDb (movies & TV series)
  - Open Library (books)
  - MusicBrainz (music)
- Full-text search across all media types
- Collection statuses: owned, watched, wishlist, in-progress, etc.
- Ratings and private notes
- Activity timeline

## Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   cd YourMediaCollection
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and set your passwords and API keys
   ```

3. **Start services**
   ```bash
   docker compose up -d postgres neo4j redis
   ```

4. **Wait for services to be healthy** (check with `docker compose ps`)

5. **Run migrations** (when backend is added to docker compose)
   ```bash
   docker compose exec backend python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

7. **Sync initial media data**
   ```bash
   docker compose exec backend python manage.py sync_tmdb --limit 100
   docker compose exec backend python manage.py sync_openlibrary --limit 100
   ```

### Local Development Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Docker services**
   ```bash
   docker compose up -d postgres neo4j redis
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **API Documentation**
   - Swagger UI: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/

## Project Structure

```
YourMediaCollection/
├── yourmedia/              # Django project settings
│   ├── settings/          # Environment-specific settings
│   ├── urls.py           # URL routing
│   └── celery.py         # Celery configuration
├── apps/                  # Django applications
│   ├── accounts/         # User management
│   ├── media_catalog/    # Media models (Movie, Book, Music, etc.)
│   ├── collections/      # User collections (UserMedia)
│   ├── data_sync/        # External API integrations
│   ├── social/           # [Phase 2] Social features
│   └── recommendations/  # [Phase 2] Recommendation engine
├── core/                  # Shared utilities
│   └── services/         # Neo4j service layer
├── docker-compose.yml     # Docker services
└── requirements.txt       # Python dependencies
```

## Database Schema

### PostgreSQL Tables

- `accounts_user`: User accounts
- `media_catalog_media`: Base media table (polymorphic)
- `media_catalog_movie`: Movie-specific fields
- `media_catalog_book`: Book-specific fields
- `media_catalog_music`: Music-specific fields
- `media_catalog_concert`: User-created concerts
- `media_catalog_document`: User-created documents
- `collections_usermedia`: User's media collection with statuses

### Neo4j Graph

- **Nodes**: User, Media, Genre
- **Relationships**: OWNS, WATCHED, WISHES, IN_PROGRESS, HAS_GENRE

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get JWT token)
- `POST /api/auth/refresh/` - Refresh JWT token

### Media Catalog
- `GET /api/media/` - List/search all media
- `GET /api/media/{id}/` - Get media details
- `GET /api/media/movies/` - List movies
- `GET /api/media/books/` - List books
- `GET /api/media/music/` - List music

### Collections
- `GET /api/collections/my/` - Get user's collection
- `POST /api/collections/` - Add media to collection
- `PATCH /api/collections/{id}/` - Update collection item
- `DELETE /api/collections/{id}/` - Remove from collection

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Celery Worker (for async tasks)

```bash
celery -A yourmedia worker -l info
```

### Celery Beat (for scheduled tasks)

```bash
celery -A yourmedia beat -l info
```

## External APIs

### TMDb (Movies & TV)
- Sign up at https://www.themoviedb.org/
- Get API key from https://www.themoviedb.org/settings/api
- Add to `.env`: `TMDB_API_KEY=your_key_here`

### Open Library (Books)
- No API key required
- Free and open-source

### MusicBrainz (Music)
- No API key required
- Rate limit: 1 request/second

## Roadmap

- [x] Phase 1: Personal media collection
- [ ] Phase 2: Enhanced features (timeline, statistics, advanced search)
- [ ] Phase 3: Social features (friends, recommendations, groups)
- [ ] Phase 4: Mobile app

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

This means:
- ✅ You can use, modify, and distribute this software
- ✅ You must make your source code available under AGPL-3.0
- ✅ If you run a modified version as a web service, you must provide the source code to users
- ✅ Any derivative work must also be licensed under AGPL-3.0

See the [LICENSE](LICENSE) file for full details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

By contributing, you agree that your contributions will be licensed under the same AGPL-3.0 license.
