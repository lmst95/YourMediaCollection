from django import forms
from .models import BookRating


class BookSearchForm(forms.Form):
    """Form for searching and importing books from DNB"""

    SEARCH_TYPE_CHOICES = [
        ('isbn', 'ISBN'),
        ('title', 'Titel'),
        ('author', 'Autor (Format: Nachname, Vorname)'),
        ('keyword', 'Stichwort/Allgemein'),
    ]

    SORT_CHOICES = [
        ('', 'Keine Sortierung'),
        ('title', 'Titel (A-Z)'),
        ('-title', 'Titel (Z-A)'),
        ('authors', 'Autor (A-Z)'),
        ('-authors', 'Autor (Z-A)'),
        ('publication_year', 'Jahr (aufsteigend)'),
        ('-publication_year', 'Jahr (absteigend)'),
        ('page_count', 'Seiten (aufsteigend)'),
        ('-page_count', 'Seiten (absteigend)'),
    ]

    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label='Suchtyp',
        initial='isbn'
    )

    query = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'placeholder': 'z.B. 978-3-446-45873-1 oder Beckett, Simon',
            'class': 'search-input'
        }),
        label='Suche'
    )

    max_results = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'number-input'
        }),
        label='Max. Ergebnisse'
    )

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='',
        widget=forms.Select(attrs={
            'class': 'sort-select'
        }),
        label='Sortierung'
    )


class BookRatingForm(forms.ModelForm):
    """Form for rating books (1-5 stars) with optional review"""

    class Meta:
        model = BookRating
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, '⭐' * i) for i in range(1, 6)],
                attrs={'class': 'star-rating'}
            ),
            'review_text': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Optionale Rezension...'
            })
        }
        labels = {
            'rating': 'Bewertung',
            'review_text': 'Rezension'
        }


class BookReadStatusForm(forms.Form):
    """Form for toggling read status of a book"""

    is_read = forms.BooleanField(
        required=False,
        label='Als gelesen markieren',
        widget=forms.CheckboxInput(attrs={'class': 'read-status-checkbox'})
    )

    read_date = forms.DateField(
        required=False,
        label='Gelesen am',
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'read-date-input'
            }
        ),
        input_formats=['%Y-%m-%d']
    )
