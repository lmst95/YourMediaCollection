import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.todos.models import Todo
from apps.todos.forms import TodoForm

User = get_user_model()

user = User.objects.get(username='testuser')
todo = Todo.objects.filter(user=user).first()

print(f"User: {user.username}")
print(f"Todo: {todo.title if todo else 'None'}")
print()

# Test form with user context
form = TodoForm(user=user, instance=todo)

print(f"Books queryset count: {form.fields['linked_books'].queryset.count()}")
print(f"Documents queryset count: {form.fields['linked_documents'].queryset.count()}")
print(f"Collections queryset count: {form.fields['linked_collections'].queryset.count()}")
print()

print("Books:")
for book in form.fields['linked_books'].queryset[:5]:
    print(f"  - {book}")

print("\nDocuments:")
for doc in form.fields['linked_documents'].queryset[:5]:
    print(f"  - {doc}")

print("\nCollections:")
for col in form.fields['linked_collections'].queryset[:5]:
    print(f"  - {col}")
