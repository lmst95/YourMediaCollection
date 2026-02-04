from django import forms
from .models import Todo, TodoItem
from apps.books.models import Book
from apps.documents.models import Document
from apps.user_collections.models import Collection
from django.contrib.contenttypes.models import ContentType


class TodoForm(forms.ModelForm):
    """Form for creating and updating todos"""

    # Additional fields for linking items (querysets will be set in __init__)
    linked_books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Verknüpfte Bücher'
    )

    linked_documents = forms.ModelMultipleChoiceField(
        queryset=Document.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Verknüpfte Dokumente'
    )

    linked_collections = forms.ModelMultipleChoiceField(
        queryset=Collection.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Verknüpfte Sammlungen'
    )

    class Meta:
        model = Todo
        fields = ['title', 'description', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Titel der Aufgabe...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Beschreibung (optional)...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set querysets for user-specific items
        if user:
            # Books are shared across all users (from DNB), so we show all
            self.fields['linked_books'].queryset = Book.objects.all()
            # Documents and collections are user-specific
            self.fields['linked_documents'].queryset = Document.objects.filter(user=user)
            self.fields['linked_collections'].queryset = Collection.objects.filter(user=user)

        # Pre-populate linked items if editing existing todo
        if self.instance.pk:
            # Get existing linked items
            book_ct = ContentType.objects.get_for_model(Book)
            document_ct = ContentType.objects.get_for_model(Document)
            collection_ct = ContentType.objects.get_for_model(Collection)

            linked_books = TodoItem.objects.filter(
                todo=self.instance,
                content_type=book_ct
            ).values_list('object_id', flat=True)

            linked_documents = TodoItem.objects.filter(
                todo=self.instance,
                content_type=document_ct
            ).values_list('object_id', flat=True)

            linked_collections = TodoItem.objects.filter(
                todo=self.instance,
                content_type=collection_ct
            ).values_list('object_id', flat=True)

            self.fields['linked_books'].initial = Book.objects.filter(id__in=linked_books)
            self.fields['linked_documents'].initial = Document.objects.filter(id__in=linked_documents)
            self.fields['linked_collections'].initial = Collection.objects.filter(id__in=linked_collections)

    def save(self, commit=True):
        todo = super().save(commit=commit)

        if commit:
            # Clear existing linked items
            TodoItem.objects.filter(todo=todo).delete()

            # Add linked books
            book_ct = ContentType.objects.get_for_model(Book)
            for book in self.cleaned_data['linked_books']:
                TodoItem.objects.create(
                    todo=todo,
                    content_type=book_ct,
                    object_id=book.id
                )

            # Add linked documents
            document_ct = ContentType.objects.get_for_model(Document)
            for document in self.cleaned_data['linked_documents']:
                TodoItem.objects.create(
                    todo=todo,
                    content_type=document_ct,
                    object_id=document.id
                )

            # Add linked collections
            collection_ct = ContentType.objects.get_for_model(Collection)
            for collection in self.cleaned_data['linked_collections']:
                TodoItem.objects.create(
                    todo=todo,
                    content_type=collection_ct,
                    object_id=collection.id
                )

        return todo
