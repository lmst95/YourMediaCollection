from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    """Form for creating and editing documents"""

    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'file_type', 'authors', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Titel des Dokuments...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Beschreibung (optional)...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': '.pdf,.epub,.mobi,.txt,.doc,.docx'
            }),
            'file_type': forms.Select(attrs={
                'class': 'form-input'
            }),
        }

    # We'll handle authors and categories as comma-separated input
    authors_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Autoren (durch Komma getrennt)...'
        }),
        label='Autoren'
    )

    categories_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Kategorien (durch Komma getrennt)...'
        }),
        label='Kategorien'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the original JSONField widgets
        self.fields.pop('authors', None)
        self.fields.pop('categories', None)

        # Pre-populate text fields if editing
        if self.instance.pk:
            if self.instance.authors:
                self.fields['authors_input'].initial = ', '.join(self.instance.authors)
            if self.instance.categories:
                self.fields['categories_input'].initial = ', '.join(self.instance.categories)

            # Make file optional when editing
            self.fields['file'].required = False

    def clean_authors_input(self):
        authors_str = self.cleaned_data.get('authors_input', '')
        if authors_str:
            return [author.strip() for author in authors_str.split(',') if author.strip()]
        return []

    def clean_categories_input(self):
        categories_str = self.cleaned_data.get('categories_input', '')
        if categories_str:
            return [cat.strip() for cat in categories_str.split(',') if cat.strip()]
        return []

    def save(self, commit=True):
        document = super().save(commit=False)

        # Set authors and categories from text input
        document.authors = self.cleaned_data.get('authors_input') or []
        document.categories = self.cleaned_data.get('categories_input') or []

        # Set file size if file is present
        if self.cleaned_data.get('file'):
            document.file_size = self.cleaned_data['file'].size

        if commit:
            document.save()

        return document
