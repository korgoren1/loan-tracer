# core/forms.py

from .models import MoneyOut
from django import forms
from .models import Client
from django.utils import timezone
from .models import TYPE_CHOICES
# core/forms.py

from django import forms
from .models import Client, MoneyOut, Loan, Payment, OpeningBalance, TYPE_CHOICES

class LoanForm(forms.Form):
    client_name = forms.CharField(label="Client Name")
    amount = forms.FloatField(label="Loan Amount")
    date = forms.DateField(label="Loan Date", widget=forms.DateInput(attrs={'type': 'date'}))

class PaymentForm(forms.Form):
    client_name = forms.CharField(label="Client Name")
    amount = forms.FloatField(label="Payment Amount")
    date = forms.DateField(label="Payment Date", widget=forms.DateInput(attrs={'type': 'date'}))

class MoneyOutForm(forms.ModelForm):
    class Meta:
        model = MoneyOut
        fields = ['amount', 'date', 'type', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class OpeningBalanceForm(forms.ModelForm):
    class Meta:
        model = OpeningBalance
        fields = ['amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

# Optional: for later use if allowing full client creation form
class ClientForm(forms.Form):
    name = forms.CharField(label="New Client Name")