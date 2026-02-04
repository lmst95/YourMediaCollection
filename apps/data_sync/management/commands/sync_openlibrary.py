"""
Management command to sync books from Open Library API.
Usage: python manage.py sync_openlibrary --limit 50
"""

import requests
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.media_catalog.models import Media, MediaType, Book
from apps.data_sync.models import SyncTask


class Command(BaseCommand):
    help = 'Sync books from Open Library API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Number of books to fetch (default: 20)',
        )
        parser.add_argument(
            '--subject',
            type=str,
            default='fiction',
            help='Subject to search (default: fiction). Examples: fantasy, science_fiction, mystery, history',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        subject = options['subject']

        self.stdout.write(self.style.SUCCESS(
            f'Starting Open Library sync (subject: {subject}, limit: {limit})'
        ))

        self.sync_books(subject, limit)

        self.stdout.write(self.style.SUCCESS('Open Library sync completed!'))

    def sync_books(self, subject, limit):
        """Sync books from Open Library."""
        self.stdout.write(f'Syncing books from Open Library (subject: {subject})...')

        base_url = 'https://openlibrary.org'
        synced_count = 0
        skipped_count = 0

        # Create sync task
        sync_task = SyncTask.objects.create(
            source='openlibrary',
            media_type='book',
            status='running'
        )

        try:
            # Get subject works
            subject_url = f'{base_url}/subjects/{subject}.json'
            params = {
                'limit': limit * 2,  # Fetch more to account for duplicates and missing data
            }

            try:
                response = requests.get(subject_url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'API request failed: {e}'))
                sync_task.status = 'failed'
                sync_task.errors.append({'error': str(e)})
                sync_task.save()
                return

            works = data.get('works', [])

            for work_data in works:
                if synced_count >= limit:
                    break

                # Rate limit: Open Library requests 1 req/sec
                time.sleep(1)

                work_key = work_data.get('key')
                if not work_key:
                    continue

                # Extract Open Library ID from key (e.g., '/works/OL45804W' -> 'OL45804W')
                ol_id = work_key.split('/')[-1]

                # Check if book already exists
                if Book.objects.filter(openlibrary_id=ol_id).exists():
                    skipped_count += 1
                    continue

                # Get work details
                work_url = f'{base_url}{work_key}.json'
                try:
                    work_response = requests.get(work_url, timeout=10)
                    work_response.raise_for_status()
                    work_detail = work_response.json()
                except requests.RequestException as e:
                    self.stdout.write(self.style.WARNING(f'Failed to get work details for {work_key}: {e}'))
                    continue

                # Try to get an edition to get more details (ISBN, pages, etc.)
                edition_data = None
                editions_url = f'{base_url}{work_key}/editions.json'
                try:
                    editions_response = requests.get(editions_url, params={'limit': 1}, timeout=10)
                    editions_response.raise_for_status()
                    editions_result = editions_response.json()
                    entries = editions_result.get('entries', [])
                    if entries:
                        edition_data = entries[0]
                except requests.RequestException:
                    pass  # Edition details are optional

                # Create book
                try:
                    with transaction.atomic():
                        book = self._create_book(work_detail, edition_data, ol_id)
                        if book:
                            synced_count += 1
                            title = work_detail.get('title', 'Unknown')
                            self.stdout.write(f'  ✓ Synced: {title}')
                        else:
                            skipped_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to create book: {e}'))
                    sync_task.errors.append({'ol_id': ol_id, 'error': str(e)})

            # Update sync task
            sync_task.status = 'completed'
            sync_task.records_processed = synced_count
            sync_task.last_sync_at = datetime.now()
            sync_task.save()

            self.stdout.write(self.style.SUCCESS(
                f'Books: {synced_count} synced, {skipped_count} skipped (already exist or missing data)'
            ))

        except Exception as e:
            sync_task.status = 'failed'
            sync_task.errors.append({'error': str(e)})
            sync_task.save()
            raise

    def _create_book(self, work_data, edition_data, ol_id):
        """Create a Book instance from Open Library data."""
        title = work_data.get('title')
        if not title:
            return None

        # Get description
        description = ''
        if isinstance(work_data.get('description'), str):
            description = work_data.get('description', '')
        elif isinstance(work_data.get('description'), dict):
            description = work_data.get('description', {}).get('value', '')

        # Get first publish date
        first_publish_date = work_data.get('first_publish_date')
        release_date = None
        if first_publish_date:
            # Try to parse year from string like "1813", "January 28, 1813", etc.
            try:
                # Try full date first
                release_date = datetime.strptime(first_publish_date, '%B %d, %Y').date()
            except (ValueError, TypeError):
                try:
                    # Try just year
                    year = int(first_publish_date[:4])
                    release_date = datetime(year, 1, 1).date()
                except (ValueError, TypeError):
                    pass

        # Get cover image
        cover_id = work_data.get('covers', [None])[0]
        cover_url = ''
        if cover_id:
            cover_url = f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg'

        # Get authors
        authors = []
        for author_ref in work_data.get('authors', []):
            author_key = author_ref.get('author', {}).get('key', '')
            if author_key:
                # Try to get author name from the work data (sometimes it's included)
                author_name = author_ref.get('name')
                if author_name:
                    authors.append(author_name)

        # Get subjects/genres (take first 5)
        subjects = work_data.get('subjects', [])[:5]

        # Get ISBN and other details from edition if available
        isbn = ''
        publisher = ''
        page_count = None
        language = 'en'  # Default to English

        if edition_data:
            # Get ISBN (prefer ISBN-13, then ISBN-10)
            isbn_13 = edition_data.get('isbn_13', [])
            isbn_10 = edition_data.get('isbn_10', [])
            if isbn_13:
                isbn = isbn_13[0]
            elif isbn_10:
                isbn = isbn_10[0]

            # Get publisher
            publishers = edition_data.get('publishers', [])
            if publishers:
                publisher = publishers[0]

            # Get page count
            page_count = edition_data.get('number_of_pages')

            # Get language
            languages = edition_data.get('languages', [])
            if languages:
                lang_key = languages[0].get('key', '')
                # Extract language code from key like '/languages/eng'
                if '/' in lang_key:
                    language = lang_key.split('/')[-1][:2]

        # Create Book (automatically creates Media parent via multi-table inheritance)
        book = Book.objects.create(
            # Media fields
            media_type=MediaType.BOOK,
            title=title,
            description=description,
            release_date=release_date,
            cover_image_url=cover_url,
            genres=subjects,
            external_ids={
                'openlibrary_id': ol_id,
                'isbn': isbn,
            },
            metadata={
                'work_key': work_data.get('key', ''),
                'edition_count': work_data.get('edition_count', 0),
            },
            is_public=True,
            # Book-specific fields
            authors=authors,
            isbn=isbn if isbn else None,
            publisher=publisher,
            page_count=page_count,
            language=language,
            openlibrary_id=ol_id,
        )

        return book
