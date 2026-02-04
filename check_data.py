import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.documents.models import Document
from apps.user_collections.models import Collection
from apps.books.models import Book

User = get_user_model()

try:
    user = User.objects.get(username='testuser')
    print(f"User: {user.username}")
    print(f"\nDocuments: {Document.objects.filter(user=user).count()}")
    print(f"Collections: {Collection.objects.filter(user=user).count()}")
    print(f"Books (total): {Book.objects.count()}")

    print("\n--- Documents ---")
    for doc in Document.objects.filter(user=user)[:10]:
        print(f"  - [{doc.id}] {doc.title}")

    print("\n--- Collections ---")
    for col in Collection.objects.filter(user=user)[:10]:
        print(f"  - [{col.id}] {col.name}")

    print("\n--- Books ---")
    for book in Book.objects.all()[:10]:
        print(f"  - [{book.id}] {book.title}")

except User.DoesNotExist:
    print("User 'testuser' does not exist")
