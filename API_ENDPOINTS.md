API Endpoints Reference

## Base URL
- Development: `http://localhost:8000/api/`
- API Documentation: `http://localhost:8000/api/docs/` (Swagger UI)
- Alternative Docs: `http://localhost:8000/api/redoc/` (ReDoc)

---

## Authentication

### Register
**POST** `/api/auth/register/`

Create a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "password_confirm": "secure_password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    ...
  },
  "message": "User registered successfully. Please login to continue."
}
```

### Login
**POST** `/api/auth/login/`

Obtain JWT access and refresh tokens.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
**POST** `/api/auth/refresh/`

Refresh the JWT access token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## User Profile

### Get Current User
**GET** `/api/auth/users/me/`

🔒 Requires authentication

Get the authenticated user's profile.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Movie enthusiast",
  "preferences": {},
  "date_joined": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Update Profile
**PATCH** `/api/auth/users/me/`

🔒 Requires authentication

Update the authenticated user's profile.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

### Change Password
**POST** `/api/auth/users/password/change/`

🔒 Requires authentication

Change the user's password.

**Request Body:**
```json
{
  "old_password": "current_password",
  "new_password": "new_secure_password",
  "new_password_confirm": "new_secure_password"
}
```

### Get User by ID
**GET** `/api/auth/users/{id}/`

Get public profile of a specific user.

---

## Media Catalog

### List All Media
**GET** `/api/media/`

Get a paginated list of all media items.

**Query Parameters:**
- `media_type` (optional): Filter by type (movie, tv_series, book, music, concert, document)
- `genre` (optional): Filter by genre
- `release_year` (optional): Filter by release year
- `title_contains` (optional): Search in title
- `search` (optional): Full-text search in title and description
- `ordering` (optional): Sort by field (e.g., `-release_date`, `title`)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Example:** `GET /api/media/?media_type=movie&genre=Action&ordering=-release_date`

**Response:** `200 OK`
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/media/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "media_type": "movie",
      "media_type_display": "Movie",
      "title": "Inception",
      "release_date": "2010-07-16",
      "cover_image_url": "https://...",
      "genres": ["Action", "Sci-Fi", "Thriller"]
    },
    ...
  ]
}
```

### Get Media Details
**GET** `/api/media/{id}/`

Get detailed information about a specific media item.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "media_type": "movie",
  "media_type_display": "Movie",
  "title": "Inception",
  "description": "A thief who steals corporate secrets...",
  "release_date": "2010-07-16",
  "cover_image_url": "https://...",
  "genres": ["Action", "Sci-Fi", "Thriller"],
  "external_ids": {
    "tmdb_id": 27205,
    "imdb_id": "tt1375666"
  },
  "runtime_minutes": 148,
  "director": "Christopher Nolan",
  "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
  "tmdb_id": 27205,
  "imdb_id": "tt1375666",
  "is_public": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Create Custom Media
**POST** `/api/media/create/`

🔒 Requires authentication

Create a custom media entry (concert, document).

**Request Body:**
```json
{
  "media_type": "concert",
  "title": "Coldplay Live 2024",
  "description": "Amazing concert experience",
  "genres": ["Rock", "Pop"],
  "artist": "Coldplay",
  "venue": "Madison Square Garden",
  "location": "New York, USA",
  "event_date": "2024-06-15"
}
```

### List Movies
**GET** `/api/media/movies/`

Get a list of movies (filtered by media_type=movie).

### List TV Series
**GET** `/api/media/tv-series/`

Get a list of TV series.

### List Books
**GET** `/api/media/books/`

Get a list of books.

### List Music
**GET** `/api/media/music/`

Get a list of music albums.

### Get Genres
**GET** `/api/media/genres/`

Get a list of all available genres.

**Response:** `200 OK`
```json
{
  "genres": [
    "Action",
    "Adventure",
    "Comedy",
    "Drama",
    "Horror",
    "Romance",
    "Sci-Fi",
    "Thriller"
  ]
}
```

---

## Collections

### Get My Collection
**GET** `/api/collections/my/`

🔒 Requires authentication

Get the authenticated user's media collection.

**Query Parameters:**
- `status` (optional): Filter by status (owned, watched, read, listened, wishlist, borrowed, lent, in_progress)

**Example:** `GET /api/collections/my/?status=wishlist`

**Response:** `200 OK`
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "user": "user_uuid",
      "user_username": "john_doe",
      "media": "media_uuid",
      "media_details": {
        "id": "media_uuid",
        "title": "Inception",
        "media_type": "movie",
        "cover_image_url": "https://...",
        "genres": ["Action", "Sci-Fi"]
      },
      "status": "watched",
      "status_display": "Watched",
      "rating": 9.5,
      "notes": "Amazing movie!",
      "added_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-20T22:00:00Z",
      "updated_at": "2024-01-20T22:00:00Z"
    },
    ...
  ]
}
```

### Add to Collection
**POST** `/api/collections/`

🔒 Requires authentication

Add a media item to your collection.

**Request Body:**
```json
{
  "media": "media_uuid",
  "status": "owned",
  "rating": 8.5,
  "notes": "Great book, highly recommend!",
  "completed_at": "2024-01-20T22:00:00Z"
}
```

**Response:** `201 Created`

### Get Collection Item
**GET** `/api/collections/{id}/`

🔒 Requires authentication

Get details of a specific item in your collection.

### Update Collection Item
**PATCH** `/api/collections/{id}/`

🔒 Requires authentication

Update status, rating, or notes for a collection item.

**Request Body:**
```json
{
  "status": "watched",
  "rating": 9.0,
  "notes": "Updated notes",
  "completed_at": "2024-01-22T20:00:00Z"
}
```

### Remove from Collection
**DELETE** `/api/collections/{id}/`

🔒 Requires authentication

Remove a media item from your collection.

**Response:** `204 No Content`

### Collection Statistics
**GET** `/api/collections/stats/`

🔒 Requires authentication

Get statistics about your collection.

**Response:** `200 OK`
```json
{
  "total_items": 150,
  "by_type": {
    "movie": 60,
    "book": 45,
    "tv_series": 30,
    "music": 15
  },
  "by_status": {
    "owned": 80,
    "watched": 40,
    "wishlist": 20,
    "in_progress": 10
  },
  "average_rating": 7.85
}
```

### Collection Timeline
**GET** `/api/collections/timeline/`

🔒 Requires authentication

Get a timeline of recent collection activities (last 50 items).

---

## Authentication Header

For all 🔒 authenticated endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error."
}
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Data Sync Endpoints (Admin Only)

*Coming in Phase 1, Week 3*

- `POST /api/sync/tmdb/` - Trigger TMDb sync
- `POST /api/sync/openlibrary/` - Trigger OpenLibrary sync
- `POST /api/sync/musicbrainz/` - Trigger MusicBrainz sync
- `GET /api/sync/status/` - Check sync status

---

## Testing with Swagger UI

Visit `http://localhost:8000/api/docs/` for interactive API documentation where you can:
1. View all endpoints
2. Try out API calls
3. Authenticate with JWT tokens
4. See request/response examples

---

**Last Updated:** 2026-01-15
