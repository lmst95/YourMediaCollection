# Book Import Guide - Quick Start

Your media collection now has a complete book import system that fetches metadata from the Deutsche Nationalbibliothek (DNB) API.

## ✅ What's Been Set Up

1. **DNB API Client** ([apps/books/dnb_api.py](apps/books/dnb_api.py))
   - Fetches book metadata from DNB
   - Supports search by title, author, ISBN, and more
   - Parses MARC21 XML format

2. **Management Commands**
   - `import_books` - Search and import books
   - `import_books_from_file` - Bulk import from ISBN list

3. **Book Overview Page** ([/books/](http://127.0.0.1:8000/books/))
   - Browse all imported books
   - Search by title, author, ISBN
   - Filter by year and category
   - Add books to collections directly from the list

## 🚀 Quick Start Examples

### Import a Single Book by ISBN

```bash
python manage.py import_books --isbn 978-3-446-45873-1
```

### Search and Import Books

```bash
# Search for Python programming books
python manage.py import_books --query "tit=Python" --max-records 10

# Search by author
python manage.py import_books --query "atr=Martin Fowler" --max-records 5

# Combined search (Python books from 2023)
python manage.py import_books --query "tit=Python AND jhr=2023" --max-records 20
```

### Bulk Import from File

Create a file `my_books.txt`:
```
978-3-446-45873-1
978-3-8362-7017-8
978-3-95845-123-4
```

Then import:
```bash
python manage.py import_books_from_file my_books.txt
```

### Sample Books Included

A [sample_books.txt](sample_books.txt) file is included with popular German tech book ISBNs. Import them:

```bash
python manage.py import_books_from_file sample_books.txt
```

## 🔍 DNB Search Query Examples

| What you want | Query |
|---------------|-------|
| Books about Python | `tit=Python` |
| Books by author | `atr=Martin Fowler` |
| Books from 2023 | `jhr=2023` |
| Specific publisher | `pub=O'Reilly` |
| Subject area | `sub=Programming` |
| Combine searches | `tit=Django AND jhr>=2022` |

## 📚 Using the Web Interface

1. **Browse Books**: Visit `/books/` to see all imported books
2. **Search**: Use the search bar to find books by title, author, or ISBN
3. **Filter**: Filter by publication year or category
4. **Sort**: Sort by title, year, or rating
5. **Add to Collection**: Click "Zu Sammlung" to add any book to your collections

## 📖 Detailed Documentation

For complete documentation including:
- Advanced search syntax
- API client usage
- Troubleshooting
- Building a book collection

See: [apps/books/README_DNB_IMPORT.md](apps/books/README_DNB_IMPORT.md)

## 🔧 Common Commands

```bash
# Import specific book
python manage.py import_books --isbn 978-3-446-45873-1

# Search and import
python manage.py import_books --query "tit=Python Programming" --max-records 5

# Bulk import from file
python manage.py import_books_from_file my_books.txt

# Update existing books
python manage.py import_books --query "tit=Python" --update

# With slower API requests (polite mode)
python manage.py import_books_from_file books.txt --delay 1.0
```

## ⚠️ Important Notes

- **DNB Focus**: The DNB primarily contains German-speaking publications
- **Rate Limiting**: Use `--delay` for bulk imports to be respectful of the API
- **Duplicates**: Books are identified by DNB ID - duplicates are skipped automatically
- **Unicode Issues**: Windows console may have display issues with special characters, but data is stored correctly

## 🎯 Next Steps

1. Import your first books using one of the methods above
2. Visit `/books/` to see your collection
3. Use the search and filters to find books
4. Add books to your personal collections
5. Build up your library gradually

Happy collecting!
