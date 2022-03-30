from django import forms
from .models import Characteristics
from Django_Online_Shop.settings import DB_TRANSFER


class ItemsPerPageForm(forms.Form):
    CHOICES = (
        (6, 6),
        (12, 12)
    )
    Items_per_page = forms.ChoiceField(label='Items per page:', label_suffix='', choices=CHOICES, widget=forms.Select(attrs={'onchange': 'this.form.submit()'}))

class MainFilter(forms.Form):
    if not DB_TRANSFER:
        chars = Characteristics.objects.all().values("name")
        CHOICES = []
        for char in chars:
            CHOICES.append([char['name'], char['name']])
        CHOICES = tuple(CHOICES)
        characteristics = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
