"""
Management command to sync music albums from MusicBrainz API.
Usage: python manage.py sync_musicbrainz --limit 50
"""

import requests
import time
import uuid as uuid_lib
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.media_catalog.models import Media, MediaType, Music, MusicAlbumType
from apps.data_sync.models import SyncTask


class Command(BaseCommand):
    help = 'Sync music albums from MusicBrainz API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Number of albums to fetch (default: 20)',
        )
        parser.add_argument(
            '--query',
            type=str,
            default='',
            help='Search query (artist or album name). If empty, fetches popular releases.',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        query = options['query']

        self.stdout.write(self.style.SUCCESS(f'Starting MusicBrainz sync (limit: {limit})'))

        self.sync_music(query, limit)

        self.stdout.write(self.style.SUCCESS('MusicBrainz sync completed!'))

    def sync_music(self, query, limit):
        """Sync music albums from MusicBrainz."""
        self.stdout.write('Syncing music from MusicBrainz...')

        base_url = 'https://musicbrainz.org/ws/2'
        synced_count = 0
        skipped_count = 0

        # Create sync task
        sync_task = SyncTask.objects.create(
            source='musicbrainz',
            media_type='music',
            status='running'
        )

        try:
            # Search for release groups (albums)
            # If no query, use a broad search for popular albums
            search_query = query if query else 'type:album AND status:official'

            params = {
                'query': search_query,
                'limit': limit * 2,  # Fetch more to account for duplicates
                'fmt': 'json',
            }

            headers = {
                'User-Agent': 'YourMediaCollection/1.0 (https://github.com/yourusername/yourmedia)',
            }

            try:
                # MusicBrainz rate limit: 1 request per second
                url = f'{base_url}/release-group'
                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'API request failed: {e}'))
                sync_task.status = 'failed'
                sync_task.errors.append({'error': str(e)})
                sync_task.save()
                return

            release_groups = data.get('release-groups', [])

            for rg_data in release_groups:
                if synced_count >= limit:
                    break

                # Rate limit: 1 request per second
                time.sleep(1)

                mb_id = rg_data.get('id')
                if not mb_id:
                    continue

                try:
                    mb_uuid = uuid_lib.UUID(mb_id)
                except (ValueError, TypeError):
                    continue

                # Check if album already exists
                if Music.objects.filter(musicbrainz_id=mb_uuid).exists():
                    skipped_count += 1
                    continue

                # Get detailed release group information
                detail_url = f'{base_url}/release-group/{mb_id}'
                detail_params = {
                    'inc': 'artists+releases+genres+tags',
                    'fmt': 'json',
                }

                try:
                    detail_response = requests.get(
                        detail_url,
                        params=detail_params,
                        headers=headers,
                        timeout=10
                    )
                    detail_response.raise_for_status()
                    detail_data = detail_response.json()
                except requests.RequestException as e:
                    self.stdout.write(self.style.WARNING(f'Failed to get details for {mb_id}: {e}'))
                    continue

                # Get first release for additional details
                releases = detail_data.get('releases', [])
                first_release_data = None
                if releases:
                    release_id = releases[0].get('id')
                    if release_id:
                        time.sleep(1)  # Rate limit
                        try:
                            release_url = f'{base_url}/release/{release_id}'
                            release_params = {
                                'inc': 'labels+recordings',
                                'fmt': 'json',
                            }
                            release_response = requests.get(
                                release_url,
                                params=release_params,
                                headers=headers,
                                timeout=10
                            )
                            release_response.raise_for_status()
                            first_release_data = release_response.json()
                        except requests.RequestException:
                            pass  # Release details are optional

                # Create music album
                try:
                    with transaction.atomic():
                        music = self._create_music(detail_data, first_release_data, mb_uuid)
                        if music:
                            synced_count += 1
                            title = detail_data.get('title', 'Unknown')
                            self.stdout.write(f'  ✓ Synced: {title}')
                        else:
                            skipped_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to create music: {e}'))
                    sync_task.errors.append({'mb_id': mb_id, 'error': str(e)})

            # Update sync task
            sync_task.status = 'completed'
            sync_task.records_processed = synced_count
            sync_task.last_sync_at = datetime.now()
            sync_task.save()

            self.stdout.write(self.style.SUCCESS(
                f'Music: {synced_count} synced, {skipped_count} skipped (already exist or missing data)'
            ))

        except Exception as e:
            sync_task.status = 'failed'
            sync_task.errors.append({'error': str(e)})
            sync_task.save()
            raise

    def _create_music(self, rg_data, release_data, mb_id):
        """Create a Music instance from MusicBrainz data."""
        title = rg_data.get('title')
        if not title:
            return None

        # Get artists
        artists = []
        for artist_credit in rg_data.get('artist-credit', []):
            if 'artist' in artist_credit:
                artist_name = artist_credit['artist'].get('name', '')
                if artist_name:
                    artists.append(artist_name)

        if not artists:
            return None  # Skip if no artist

        # Get album type
        primary_type = rg_data.get('primary-type', '').lower()
        type_mapping = {
            'album': MusicAlbumType.ALBUM,
            'single': MusicAlbumType.SINGLE,
            'ep': MusicAlbumType.EP,
            'compilation': MusicAlbumType.COMPILATION,
        }
        album_type = type_mapping.get(primary_type, MusicAlbumType.ALBUM)

        # Get release date (first release date)
        release_date = None
        first_release_date = rg_data.get('first-release-date')
        if first_release_date:
            try:
                # Try full date (YYYY-MM-DD)
                release_date = datetime.strptime(first_release_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                try:
                    # Try year-month (YYYY-MM)
                    release_date = datetime.strptime(first_release_date, '%Y-%m').date()
                except (ValueError, TypeError):
                    try:
                        # Try just year (YYYY)
                        year = int(first_release_date[:4])
                        release_date = datetime(year, 1, 1).date()
                    except (ValueError, TypeError):
                        pass

        # Get genres/tags
        genres = []
        for genre in rg_data.get('genres', []):
            genre_name = genre.get('name', '')
            if genre_name:
                genres.append(genre_name.title())

        # If no genres, try tags
        if not genres:
            for tag in rg_data.get('tags', [])[:5]:  # Limit to 5 tags
                tag_name = tag.get('name', '')
                if tag_name:
                    genres.append(tag_name.title())

        # Get cover art URL (if available from release data)
        cover_url = ''
        # MusicBrainz doesn't directly provide cover art URLs in the API
        # Cover art would need to be fetched from Cover Art Archive API separately
        # For now, we'll leave it empty or could add CAA integration later

        # Get label and track info from first release
        label = ''
        track_count = None

        if release_data:
            # Get label
            label_info = release_data.get('label-info', [])
            if label_info and 'label' in label_info[0]:
                label = label_info[0]['label'].get('name', '')

            # Get track count
            media = release_data.get('media', [])
            if media:
                track_count = media[0].get('track-count')

        # Create Music (automatically creates Media parent via multi-table inheritance)
        music = Music.objects.create(
            # Media fields
            media_type=MediaType.MUSIC,
            title=title,
            description='',  # MusicBrainz doesn't provide descriptions
            release_date=release_date,
            cover_image_url=cover_url,
            genres=genres,
            external_ids={
                'musicbrainz_id': str(mb_id),
            },
            metadata={
                'primary_type': rg_data.get('primary-type', ''),
                'secondary_types': rg_data.get('secondary-types', []),
            },
            is_public=True,
            # Music-specific fields
            artists=artists,
            album_type=album_type,
            track_count=track_count,
            duration_seconds=None,  # Would need to calculate from all tracks
            label=label,
            musicbrainz_id=mb_id,
        )

        return music
