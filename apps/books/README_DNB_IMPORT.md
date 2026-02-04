# Importing Books from DNB (Deutsche Nationalbibliothek)

This guide explains how to populate your database with book metadata from the Deutsche Nationalbibliothek API.

## Overview

The system includes:
- **DNB API Client** (`dnb_api.py`): Python client for fetching book metadata
- **Management Commands**: Django commands for importing books

## Quick Start

### 1. Import a single book by ISBN

```bash
python manage.py import_books --isbn 978-3-446-45873-1
```

### 2. Search and import books by title

```bash
python manage.py import_books --query "tit=Python Programming" --max-records 5
```

### 3. Search and import books by author

```bash
python manage.py import_books --query "atr=Martin Fowler" --max-records 10
```

### 4. Import from a file of ISBNs

Create a text file `books.txt`:
```
978-3-446-45873-1
978-3-8362-7017-8
978-3-95845-123-4
# Add more ISBNs here
```

Then import:
```bash
python manage.py import_books_from_file books.txt
```

## DNB Query Syntax

The DNB uses CQL (Contextual Query Language) for searches. Here are common search patterns:

### Basic Searches

| Type | Query | Example |
|------|-------|---------|
| Title | `tit=<title>` | `tit=Python` |
| Author | `atr=<author>` | `atr=Martin Fowler` |
| ISBN | `isbn=<isbn>` | `isbn=9783446458731` |
| Keyword | `<keywords>` | `django web development` |
| Subject | `sub=<subject>` | `sub=Programming` |
| Publisher | `pub=<publisher>` | `pub=O'Reilly` |
| Year | `jhr=<year>` | `jhr=2023` |

### Combined Searches

Use `AND`, `OR`, `NOT` to combine searches:

```bash
# Books about Python published in 2023
python manage.py import_books --query "tit=Python AND jhr=2023" --max-records 20

# Books by Fowler OR Beck
python manage.py import_books --query "atr=Fowler OR atr=Beck" --max-records 10

# Python books but not for beginners
python manage.py import_books --query "tit=Python NOT tit=Beginner" --max-records 15
```

## Management Commands

### import_books

Import books from DNB by searching.

**Options:**
- `--query`: CQL search query
- `--isbn`: Import specific book by ISBN
- `--dnb-id`: Import specific book by DNB ID
- `--max-records`: Maximum number of records to import (default: 10)
- `--start-record`: Starting record for pagination (default: 1)
- `--update`: Update existing books instead of skipping them

**Examples:**

```bash
# Search for Python books
python manage.py import_books --query "tit=Python" --max-records 20

# Import with pagination (get records 21-40)
python manage.py import_books --query "tit=Django" --start-record 21 --max-records 20

# Update existing books
python manage.py import_books --query "tit=Python" --update

# Import by DNB ID
python manage.py import_books --dnb-id 123456789
```

### import_books_from_file

Import multiple books from a file.

**Options:**
- `file_path`: Path to the file (required)
- `--format`: File format (`txt` or `csv`, default: `txt`)
- `--csv-isbn-column`: Column name for ISBN in CSV (default: `isbn`)
- `--delay`: Delay between requests in seconds (default: 0.5)
- `--update`: Update existing books

**Examples:**

**Text file (one ISBN per line):**

Create `isbns.txt`:
```
978-3-446-45873-1
978-3-8362-7017-8
978-3-95845-123-4
```

Import:
```bash
python manage.py import_books_from_file isbns.txt
```

**CSV file:**

Create `books.csv`:
```csv
isbn,notes
978-3-446-45873-1,Must read
978-3-8362-7017-8,Recommended
978-3-95845-123-4,Reference
```

Import:
```bash
python manage.py import_books_from_file books.csv --format csv --csv-isbn-column isbn
```

**With custom delay (to be gentle with API):**
```bash
python manage.py import_books_from_file isbns.txt --delay 1.0
```

## Using the DNB API Client Directly

You can also use the API client in Python code:

```python
from apps.books.dnb_api import DNBClient
from apps.books.models import Book

# Create client
client = DNBClient()

# Search for books
results = client.search_books('tit=Python Programming', max_records=5)

# Get book by ISBN
book_data = client.get_by_isbn('978-3-446-45873-1')

# Get book by DNB ID
book_data = client.get_by_dnb_id('123456789')

# Create book in database
if book_data:
    book = Book.objects.create(**book_data)
    print(f"Created: {book.title}")
```

## Testing the API

Test the DNB API client:

```bash
python -c "from apps.books.dnb_api import test_dnb_client; test_dnb_client()"
```

Or in Django shell:

```bash
python manage.py shell
```

```python
from apps.books.dnb_api import DNBClient

client = DNBClient()

# Test search
results = client.search_books('Python', max_records=3)
for book in results:
    print(f"{book['title']} by {', '.join(book['authors'])}")
```

## Building a Book Collection

Here's a workflow to build an initial collection:

### 1. Create an ISBN list

Research popular books in your areas of interest and create `my_books.txt`:

```
# Programming
978-0-13-468599-1  # Clean Code
978-0-13-475759-9  # Refactoring
978-0-201-63361-0  # Design Patterns

# Python
978-1-491-91291-7  # Fluent Python
978-1-449-35573-9  # Learning Python
978-1-593-27928-8  # Automate the Boring Stuff

# Web Development
978-1-491-91866-7  # Django for Beginners
978-1-484-25827-8  # Flask Web Development
```

### 2. Import the books

```bash
python manage.py import_books_from_file my_books.txt --delay 1.0
```

### 3. Verify in admin or web interface

Visit `/books/` to see your imported books!

## Popular German Tech Books (Examples)

Here are some popular German tech book ISBNs to get started:

```bash
# Python
python manage.py import_books --isbn 978-3-446-45873-1  # Python 3
python manage.py import_books --isbn 978-3-8362-7017-8  # Python Crashkurs

# Web Development
python manage.py import_books --isbn 978-3-8362-7006-2  # JavaScript

# General Programming
python manage.py import_books --isbn 978-3-8362-6489-4  # Clean Code (German)
```

## API Limitations

- **Rate Limiting**: The DNB API has rate limits. Use the `--delay` option to avoid overwhelming the server
- **Maximum Records**: API returns max 100 records per request
- **Search Quality**: Results depend on DNB's search algorithm
- **Data Availability**: Not all books have complete metadata

## Troubleshooting

### No results found
- Try simpler search terms
- Check if the book is in DNB's catalog (mainly German-speaking publications)
- Verify ISBN format (use hyphens or without, both work)

### Connection errors
- Check internet connection
- DNB API might be temporarily unavailable
- Use `--delay` to slow down requests

### Duplicate books
- By default, existing books (by DNB ID) are skipped
- Use `--update` to update existing books with new data

## API Documentation

Full DNB SRU API documentation:
https://www.dnb.de/EN/Professionell/Metadatendienste/Datenbezug/SRU/sru_node.html

CQL Query Documentation:
https://www.loc.gov/standards/sru/cql/
