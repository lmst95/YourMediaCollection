"""
Django management command to import books from DNB API
Usage: python manage.py import_books [options]
"""

from django.core.management.base import BaseCommand, CommandError
from apps.books.models import Book
from apps.books.dnb_api import DNBClient


class Command(BaseCommand):
    help = 'Import books from Deutsche Nationalbibliothek (DNB) API'

    def add_arguments(self, parser):
        # Search options
        parser.add_argument(
            '--query',
            type=str,
            help='Search query (e.g., "tit=Python" or "atr=Martin Fowler")'
        )
        parser.add_argument(
            '--isbn',
            type=str,
            help='Import a specific book by ISBN'
        )
        parser.add_argument(
            '--dnb-id',
            type=str,
            help='Import a specific book by DNB ID'
        )
        parser.add_argument(
            '--max-records',
            type=int,
            default=10,
            help='Maximum number of records to import (default: 10)'
        )
        parser.add_argument(
            '--start-record',
            type=int,
            default=1,
            help='Starting record number for pagination (default: 1)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing books if they already exist'
        )

    def handle(self, *args, **options):
        client = DNBClient()

        # Determine which search method to use
        if options['isbn']:
            self.stdout.write(f"Fetching book by ISBN: {options['isbn']}")
            book_data = client.get_by_isbn(options['isbn'])
            books_data = [book_data] if book_data else []

        elif options['dnb_id']:
            self.stdout.write(f"Fetching book by DNB ID: {options['dnb_id']}")
            book_data = client.get_by_dnb_id(options['dnb_id'])
            books_data = [book_data] if book_data else []

        elif options['query']:
            self.stdout.write(f"Searching for: {options['query']}")
            books_data = client.search_books(
                options['query'],
                max_records=options['max_records'],
                start_record=options['start_record']
            )

        else:
            raise CommandError(
                'You must provide at least one of: --query, --isbn, or --dnb-id'
            )

        if not books_data:
            self.stdout.write(self.style.WARNING('No books found'))
            return

        # Import the books
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for book_data in books_data:
            try:
                # Check if book already exists
                existing_book = Book.objects.filter(
                    dnb_id=book_data['dnb_id']
                ).first()

                if existing_book:
                    if options['update']:
                        # Update existing book
                        for key, value in book_data.items():
                            if key != 'dnb_raw_data':  # Don't override raw data
                                setattr(existing_book, key, value)
                        existing_book.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"[UPDATED] {book_data['title']}")
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"[SKIPPED] {book_data['title']} (already exists)")
                        )
                else:
                    # Create new book
                    Book.objects.create(**book_data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"[CREATED] {book_data['title']}")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"[FAILED] {book_data.get('title', 'Unknown')}: {e}")
                )

        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Import complete!"))
        self.stdout.write(f"  Created: {created_count}")
        self.stdout.write(f"  Updated: {updated_count}")
        self.stdout.write(f"  Skipped: {skipped_count}")
        self.stdout.write(f"  Total processed: {created_count + updated_count + skipped_count}")
