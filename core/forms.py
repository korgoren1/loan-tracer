# core/forms.py

from django import forms
from .models import MoneyOut

class MoneyOutForm(forms.ModelForm):
    class Meta:
        model = MoneyOut
        fields = ['amount', 'date', 'description', 'type']
