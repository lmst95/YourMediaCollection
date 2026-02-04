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

# Test form with user context (simulating TodoUpdateView)
form = TodoForm(user=user, instance=todo)

print("Form field querysets:")
print(f"  Books: {form.fields['linked_books'].queryset.count()}")
print(f"  Documents: {form.fields['linked_documents'].queryset.count()}")
print(f"  Collections: {form.fields['linked_collections'].queryset.count()}")
print()

# Check if fields have widgets
print("Form field widgets:")
print(f"  Books widget: {form.fields['linked_books'].widget.__class__.__name__}")
print(f"  Documents widget: {form.fields['linked_documents'].widget.__class__.__name__}")
print(f"  Collections widget: {form.fields['linked_collections'].widget.__class__.__name__}")
print()

# Check form rendering (partial)
print("Testing field rendering:")
books_html = str(form['linked_books'])
docs_html = str(form['linked_documents'])
colls_html = str(form['linked_collections'])

print(f"  Books HTML length: {len(books_html)} characters")
print(f"  Documents HTML length: {len(docs_html)} characters")
print(f"  Collections HTML length: {len(colls_html)} characters")
print()

# Check if fields are "truthy" (for template conditionals)
print("Field truthiness (for template {% if %}):")
print(f"  Books: {bool(form['linked_books'])}")
print(f"  Documents: {bool(form['linked_documents'])}")
print(f"  Collections: {bool(form['linked_collections'])}")
