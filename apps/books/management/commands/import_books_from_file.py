"""
Django management command to import books from a CSV or text file
Usage: python manage.py import_books_from_file <file_path> [options]
"""

from django.core.management.base import BaseCommand, CommandError
from apps.books.models import Book
from apps.books.dnb_api import DNBClient
import csv
import time


class Command(BaseCommand):
    help = 'Import books from a CSV or text file (one ISBN per line)'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the file containing ISBNs or book data'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['txt', 'csv'],
            default='txt',
            help='File format: txt (one ISBN per line) or csv (with columns)'
        )
        parser.add_argument(
            '--csv-isbn-column',
            type=str,
            default='isbn',
            help='Column name for ISBN in CSV file (default: isbn)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay in seconds between API requests (default: 0.5)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing books if they already exist'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        client = DNBClient()

        # Read ISBNs from file
        isbns = []

        try:
            if options['format'] == 'txt':
                # Read plain text file (one ISBN per line)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        isbn = line.strip()
                        if isbn and not isbn.startswith('#'):  # Skip empty lines and comments
                            isbns.append(isbn)

            elif options['format'] == 'csv':
                # Read CSV file
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    isbn_column = options['csv_isbn_column']
                    for row in reader:
                        if isbn_column in row and row[isbn_column]:
                            isbns.append(row[isbn_column].strip())

        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")
        except Exception as e:
            raise CommandError(f"Error reading file: {e}")

        if not isbns:
            self.stdout.write(self.style.WARNING('No ISBNs found in file'))
            return

        self.stdout.write(f"Found {len(isbns)} ISBN(s) to import")
        self.stdout.write("="*50)

        # Import the books
        created_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0

        for i, isbn in enumerate(isbns, 1):
            self.stdout.write(f"\n[{i}/{len(isbns)}] Processing ISBN: {isbn}")

            try:
                # Fetch book data from DNB
                book_data = client.get_by_isbn(isbn)

                if not book_data:
                    self.stdout.write(
                        self.style.WARNING(f"  [NOT FOUND] No data found for ISBN: {isbn}")
                    )
                    failed_count += 1
                    continue

                # Check if book already exists
                existing_book = Book.objects.filter(
                    dnb_id=book_data['dnb_id']
                ).first()

                if existing_book:
                    if options['update']:
                        # Update existing book
                        for key, value in book_data.items():
                            if key != 'dnb_raw_data':
                                setattr(existing_book, key, value)
                        existing_book.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  [UPDATED] {book_data['title']}")
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"  [SKIPPED] {book_data['title']} (already exists)")
                        )
                else:
                    # Create new book
                    Book.objects.create(**book_data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  [CREATED] {book_data['title']}")
                    )

                # Add delay between requests to avoid overwhelming the API
                if i < len(isbns):
                    time.sleep(options['delay'])

            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  [FAILED] {e}")
                )

        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Import complete!"))
        self.stdout.write(f"  Created: {created_count}")
        self.stdout.write(f"  Updated: {updated_count}")
        self.stdout.write(f"  Skipped: {skipped_count}")
        self.stdout.write(f"  Failed:  {failed_count}")
        self.stdout.write(f"  Total:   {len(isbns)}")
