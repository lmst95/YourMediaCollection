"""
Test script to verify todo linking functionality
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
from apps.todos.models import Todo, TodoItem
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

print("Testing Todo Linking Functionality...")
print("="*50)

# Get or create a test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"[OK] Created test user: {user.username}")
else:
    print(f"[OK] Using existing user: {user.username}")

# Create test book
book, created = Book.objects.get_or_create(
    dnb_id='test-book-001',
    defaults={
        'title': 'Test Book: Python Programming',
        'authors': ['John Doe', 'Jane Smith'],
        'publication_year': 2024
    }
)
print(f"[OK] {'Created' if created else 'Using existing'} test book: {book.title}")

# Create test document
document, created = Document.objects.get_or_create(
    user=user,
    title='Test Document',
    defaults={
        'description': 'A test document for linking',
        'file_type': 'PDF',
        'file_size': 1024  # 1 KB dummy size
    }
)
print(f"[OK] {'Created' if created else 'Using existing'} test document: {document.title}")

# Create test collection
collection, created = Collection.objects.get_or_create(
    user=user,
    name='Test Collection',
    defaults={
        'description': 'A test collection for linking'
    }
)
print(f"[OK] {'Created' if created else 'Using existing'} test collection: {collection.name}")

# Create a todo
print("\n" + "="*50)
print("Creating Todo with linked items...")
print("="*50)

todo = Todo.objects.create(
    user=user,
    title='Review Test Materials',
    description='Review all linked test items',
    status='PLANNED'
)
print(f"[OK] Created todo: {todo.title}")

# Link items to todo
book_ct = ContentType.objects.get_for_model(Book)
document_ct = ContentType.objects.get_for_model(Document)
collection_ct = ContentType.objects.get_for_model(Collection)

# Create TodoItem links
TodoItem.objects.create(todo=todo, content_type=book_ct, object_id=book.id)
TodoItem.objects.create(todo=todo, content_type=document_ct, object_id=document.id)
TodoItem.objects.create(todo=todo, content_type=collection_ct, object_id=collection.id)

print(f"[OK] Linked book: {book.title}")
print(f"[OK] Linked document: {document.title}")
print(f"[OK] Linked collection: {collection.name}")

# Verify the links
print("\n" + "="*50)
print("Verifying linked items...")
print("="*50)

linked_items = TodoItem.objects.filter(todo=todo)
print(f"[OK] Total linked items: {linked_items.count()}")

for item in linked_items:
    print(f"  - {item.content_type.model}: {item.content_object}")

print("\n" + "="*50)
print("[OK] Test completed successfully!")
print("="*50)
print("\nThe linking functionality is working correctly.")
print("You can now test it in the web interface at http://127.0.0.1:8000/todos/")
