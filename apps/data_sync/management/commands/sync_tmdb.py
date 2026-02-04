"""
Management command to sync movies and TV series from TMDb API.
Usage: python manage.py sync_tmdb --limit 50
"""

import requests
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from apps.media_catalog.models import Media, MediaType, Movie
from apps.media_catalog.models.tvseries import TVSeries
from apps.data_sync.models import SyncTask


class Command(BaseCommand):
    help = 'Sync movies and TV series from TMDb API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Number of items to fetch per media type (default: 20)',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['movie', 'tv'],
            default=None,
            help='Sync only movies or TV series (default: both)',
        )

    def handle(self, *args, **options):
        api_key = settings.TMDB_API_KEY
        if not api_key or api_key == 'your-tmdb-api-key':
            raise CommandError(
                'TMDb API key not configured. '
                'Get your free API key from https://www.themoviedb.org/settings/api '
                'and add it to your .env file as TMDB_API_KEY=your_key_here'
            )

        limit = options['limit']
        media_type_filter = options['type']

        self.stdout.write(self.style.SUCCESS(f'Starting TMDb sync (limit: {limit})'))

        # Sync movies
        if media_type_filter in [None, 'movie']:
            self.sync_movies(api_key, limit)

        # Sync TV series
        if media_type_filter in [None, 'tv']:
            self.sync_tv_series(api_key, limit)

        self.stdout.write(self.style.SUCCESS('TMDb sync completed!'))

    def sync_movies(self, api_key, limit):
        """Sync popular movies from TMDb."""
        self.stdout.write('Syncing movies from TMDb...')

        base_url = settings.TMDB_API_BASE_URL
        pages_to_fetch = (limit // 20) + 1  # TMDb returns 20 results per page
        synced_count = 0
        skipped_count = 0

        # Create sync task
        sync_task = SyncTask.objects.create(
            source='tmdb',
            media_type='movie',
            status='running'
        )

        try:
            for page in range(1, pages_to_fetch + 1):
                if synced_count >= limit:
                    break

                # Fetch popular movies
                url = f'{base_url}/movie/popular'
                params = {
                    'api_key': api_key,
                    'page': page,
                    'language': 'en-US'
                }

                try:
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f'API request failed: {e}'))
                    sync_task.errors.append({'page': page, 'error': str(e)})
                    continue

                for movie_data in data.get('results', []):
                    if synced_count >= limit:
                        break

                    tmdb_id = movie_data.get('id')
                    if not tmdb_id:
                        continue

                    # Check if movie already exists
                    if Movie.objects.filter(tmdb_id=tmdb_id).exists():
                        skipped_count += 1
                        continue

                    # Get detailed movie information
                    detail_url = f'{base_url}/movie/{tmdb_id}'
                    detail_params = {
                        'api_key': api_key,
                        'append_to_response': 'credits'
                    }

                    try:
                        detail_response = requests.get(detail_url, params=detail_params, timeout=10)
                        detail_response.raise_for_status()
                        detail_data = detail_response.json()
                    except requests.RequestException as e:
                        self.stdout.write(self.style.WARNING(f'Failed to get details for movie {tmdb_id}: {e}'))
                        continue

                    # Create movie
                    try:
                        with transaction.atomic():
                            self._create_movie(detail_data)
                            synced_count += 1
                            self.stdout.write(f'  ✓ Synced: {detail_data.get("title")}')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ Failed to create movie: {e}'))
                        sync_task.errors.append({'tmdb_id': tmdb_id, 'error': str(e)})

            # Update sync task
            sync_task.status = 'completed'
            sync_task.records_processed = synced_count
            sync_task.last_sync_at = datetime.now()
            sync_task.save()

            self.stdout.write(self.style.SUCCESS(
                f'Movies: {synced_count} synced, {skipped_count} skipped (already exist)'
            ))

        except Exception as e:
            sync_task.status = 'failed'
            sync_task.errors.append({'error': str(e)})
            sync_task.save()
            raise

    def sync_tv_series(self, api_key, limit):
        """Sync popular TV series from TMDb."""
        self.stdout.write('Syncing TV series from TMDb...')

        base_url = settings.TMDB_API_BASE_URL
        pages_to_fetch = (limit // 20) + 1
        synced_count = 0
        skipped_count = 0

        # Create sync task
        sync_task = SyncTask.objects.create(
            source='tmdb',
            media_type='tv_series',
            status='running'
        )

        try:
            for page in range(1, pages_to_fetch + 1):
                if synced_count >= limit:
                    break

                # Fetch popular TV series
                url = f'{base_url}/tv/popular'
                params = {
                    'api_key': api_key,
                    'page': page,
                    'language': 'en-US'
                }

                try:
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f'API request failed: {e}'))
                    sync_task.errors.append({'page': page, 'error': str(e)})
                    continue

                for tv_data in data.get('results', []):
                    if synced_count >= limit:
                        break

                    tmdb_id = tv_data.get('id')
                    if not tmdb_id:
                        continue

                    # Check if TV series already exists
                    if TVSeries.objects.filter(tmdb_id=tmdb_id).exists():
                        skipped_count += 1
                        continue

                    # Get detailed TV information
                    detail_url = f'{base_url}/tv/{tmdb_id}'
                    detail_params = {
                        'api_key': api_key,
                        'append_to_response': 'credits'
                    }

                    try:
                        detail_response = requests.get(detail_url, params=detail_params, timeout=10)
                        detail_response.raise_for_status()
                        detail_data = detail_response.json()
                    except requests.RequestException as e:
                        self.stdout.write(self.style.WARNING(f'Failed to get details for TV {tmdb_id}: {e}'))
                        continue

                    # Create TV series
                    try:
                        with transaction.atomic():
                            self._create_tv_series(detail_data)
                            synced_count += 1
                            self.stdout.write(f'  ✓ Synced: {detail_data.get("name")}')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ Failed to create TV series: {e}'))
                        sync_task.errors.append({'tmdb_id': tmdb_id, 'error': str(e)})

            # Update sync task
            sync_task.status = 'completed'
            sync_task.records_processed = synced_count
            sync_task.last_sync_at = datetime.now()
            sync_task.save()

            self.stdout.write(self.style.SUCCESS(
                f'TV Series: {synced_count} synced, {skipped_count} skipped (already exist)'
            ))

        except Exception as e:
            sync_task.status = 'failed'
            sync_task.errors.append({'error': str(e)})
            sync_task.save()
            raise

    def _create_movie(self, data):
        """Create a Movie instance from TMDb data."""
        # Parse release date
        release_date = None
        if data.get('release_date'):
            try:
                release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # Get poster URL
        poster_url = ''
        if data.get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"

        # Get genres
        genres = [genre['name'] for genre in data.get('genres', [])]

        # Get director from credits
        director = ''
        credits = data.get('credits', {})
        crew = credits.get('crew', [])
        for person in crew:
            if person.get('job') == 'Director':
                director = person.get('name', '')
                break

        # Get cast
        cast = []
        for actor in credits.get('cast', [])[:10]:  # Top 10 cast members
            cast.append({
                'name': actor.get('name', ''),
                'character': actor.get('character', ''),
            })

        # Create Movie (automatically creates Media parent via multi-table inheritance)
        movie = Movie.objects.create(
            # Media fields
            media_type=MediaType.MOVIE,
            title=data.get('title', ''),
            description=data.get('overview', ''),
            release_date=release_date,
            cover_image_url=poster_url,
            genres=genres,
            external_ids={
                'tmdb_id': data.get('id'),
                'imdb_id': data.get('imdb_id', ''),
            },
            metadata={
                'budget': data.get('budget', 0),
                'revenue': data.get('revenue', 0),
                'vote_average': data.get('vote_average', 0),
                'vote_count': data.get('vote_count', 0),
                'popularity': data.get('popularity', 0),
            },
            is_public=True,
            # Movie-specific fields
            runtime_minutes=data.get('runtime'),
            director=director,
            cast=cast,
            tmdb_id=data.get('id'),
            imdb_id=data.get('imdb_id', ''),
        )

        return movie

    def _create_tv_series(self, data):
        """Create a TVSeries instance from TMDb data."""
        # Parse first air date
        first_air_date = None
        if data.get('first_air_date'):
            try:
                first_air_date = datetime.strptime(data['first_air_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # Get poster URL
        poster_url = ''
        if data.get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"

        # Get genres
        genres = [genre['name'] for genre in data.get('genres', [])]

        # Get creators
        creators = [creator['name'] for creator in data.get('created_by', [])]

        # Get cast for metadata
        cast = []
        credits = data.get('credits', {})
        for actor in credits.get('cast', [])[:10]:  # Top 10 cast members
            cast.append({
                'name': actor.get('name', ''),
                'character': actor.get('character', ''),
            })

        # Map TMDb status to our choices
        tmdb_status = data.get('status', '').lower()
        status_mapping = {
            'returning series': 'ongoing',
            'in production': 'ongoing',
            'planned': 'ongoing',
            'ended': 'ended',
            'canceled': 'cancelled',
            'cancelled': 'cancelled',
        }
        status = status_mapping.get(tmdb_status, '')

        # Create TVSeries (automatically creates Media parent via multi-table inheritance)
        tv_series = TVSeries.objects.create(
            # Media fields
            media_type=MediaType.TV_SERIES,
            title=data.get('name', ''),
            description=data.get('overview', ''),
            release_date=first_air_date,
            cover_image_url=poster_url,
            genres=genres,
            external_ids={
                'tmdb_id': data.get('id'),
            },
            metadata={
                'vote_average': data.get('vote_average', 0),
                'vote_count': data.get('vote_count', 0),
                'popularity': data.get('popularity', 0),
                'original_language': data.get('original_language', ''),
                'cast': cast,
                'episode_runtime': data.get('episode_run_time', []),
            },
            is_public=True,
            # TVSeries-specific fields
            number_of_seasons=data.get('number_of_seasons', 0),
            number_of_episodes=data.get('number_of_episodes', 0),
            status=status,
            creators=creators,
            tmdb_id=data.get('id'),
        )

        return tv_series
