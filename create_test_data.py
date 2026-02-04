"""
Create test data for testing the search/filter functionality
"""
import os
import django
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.books.models import Book
from apps.documents.models import Document
from apps.user_collections.models import Collection

User = get_user_model()

print("Creating test data for search/filter testing...")
print("="*50)

# Get or create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()

print(f"[OK] Using user: {user.username}")

# Create multiple test books
books_data = [
    {'dnb_id': 'book-001', 'title': 'Python Programming for Beginners', 'authors': ['John Smith'], 'year': 2024},
    {'dnb_id': 'book-002', 'title': 'Advanced Django Web Development', 'authors': ['Jane Doe'], 'year': 2023},
    {'dnb_id': 'book-003', 'title': 'JavaScript: The Complete Guide', 'authors': ['Bob Johnson'], 'year': 2024},
    {'dnb_id': 'book-004', 'title': 'Data Science with Python', 'authors': ['Alice Williams'], 'year': 2023},
    {'dnb_id': 'book-005', 'title': 'Machine Learning Fundamentals', 'authors': ['Charlie Brown'], 'year': 2024},
    {'dnb_id': 'book-006', 'title': 'Web Design Essentials', 'authors': ['Diana Prince'], 'year': 2023},
    {'dnb_id': 'book-007', 'title': 'Database Systems', 'authors': ['Edward Norton'], 'year': 2024},
    {'dnb_id': 'book-008', 'title': 'React and Redux in Action', 'authors': ['Frank Miller'], 'year': 2023},
]

print("\nCreating books...")
for book_data in books_data:
    book, created = Book.objects.get_or_create(
        dnb_id=book_data['dnb_id'],
        defaults={
            'title': book_data['title'],
            'authors': book_data['authors'],
            'publication_year': book_data['year']
        }
    )
    if created:
        print(f"  [OK] Created: {book.title}")

# Create multiple test documents
documents_data = [
    {'title': 'Research Paper on AI', 'type': 'PDF'},
    {'title': 'Project Documentation', 'type': 'DOCX'},
    {'title': 'Meeting Notes 2024', 'type': 'TXT'},
    {'title': 'Technical Specification', 'type': 'PDF'},
    {'title': 'User Manual', 'type': 'PDF'},
    {'title': 'Code Review Guidelines', 'type': 'DOCX'},
]

print("\nCreating documents...")
for doc_data in documents_data:
    doc, created = Document.objects.get_or_create(
        user=user,
        title=doc_data['title'],
        defaults={
            'description': f'Test document: {doc_data["title"]}',
            'file_type': doc_data['type'],
            'file_size': 1024
        }
    )
    if created:
        print(f"  [OK] Created: {doc.title}")

# Create multiple test collections
collections_data = [
    {'name': 'Programming Books', 'desc': 'Collection of programming books'},
    {'name': 'Work Documents', 'desc': 'Work-related documents'},
    {'name': 'Research Materials', 'desc': 'Research papers and studies'},
    {'name': 'Personal Library', 'desc': 'Personal reading list'},
    {'name': 'Project Resources', 'desc': 'Resources for current projects'},
]

print("\nCreating collections...")
for coll_data in collections_data:
    coll, created = Collection.objects.get_or_create(
        user=user,
        name=coll_data['name'],
        defaults={
            'description': coll_data['desc']
        }
    )
    if created:
        print(f"  [OK] Created: {coll.name}")

print("\n" + "="*50)
print("[OK] Test data created successfully!")
print("="*50)
print("\nYou can now test the search functionality at:")
print("http://127.0.0.1:8000/todos/create/")
print("\nLogin credentials:")
print("Username: testuser")
print("Password: testpass123")
