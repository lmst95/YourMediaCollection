from django import forms
from .models import Collection, CollectionItem


class CollectionForm(forms.ModelForm):
    """Form for creating and editing collections"""

    class Meta:
        model = Collection
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Name der Sammlung...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Beschreibung (optional)...'
            }),
        }


class CollectionItemForm(forms.ModelForm):
    """Form for adding/editing items in a collection"""

    # Multiple statuses as checkboxes
    statuses_field = forms.MultipleChoiceField(
        choices=CollectionItem.STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Status (mehrere auswählbar)'
    )

    class Meta:
        model = CollectionItem
        fields = ['borrowed_person_name', 'borrowed_date', 'return_date', 'personal_note']
        widgets = {
            'borrowed_person_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Name der Person...'
            }),
            'borrowed_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'return_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'personal_note': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Persönliche Notiz...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-populate statuses if editing
        if self.instance.pk and self.instance.statuses:
            self.fields['statuses_field'].initial = self.instance.statuses

        # Make borrowing fields optional
        self.fields['borrowed_person_name'].required = False
        self.fields['borrowed_date'].required = False
        self.fields['return_date'].required = False
        self.fields['personal_note'].required = False

    def save(self, commit=True):
        item = super().save(commit=False)
        # Save the statuses list
        item.statuses = self.cleaned_data.get('statuses_field', [])
        if commit:
            item.save()
        return item
