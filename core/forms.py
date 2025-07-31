
from django.utils import timezone
from django import forms
from .models import Client, MoneyOut, Loan, Payment, OpeningBalance, TYPE_CHOICES

class LoanForm(forms.ModelForm):
    client_name = forms.CharField(label="Client Name")
    amount = forms.FloatField(label="Loan Amount")
    date = forms.DateField(label="Loan Date", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Loan
        fields = ['amount', 'date']  # exclude 'client' because you're setting it manually

class PaymentForm(forms.ModelForm):
    client_name = forms.CharField(label="Client Name")
    amount = forms.FloatField(label="Payment Amount")
    date = forms.DateField(label="Payment Date", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Payment
        fields = ['amount', 'date']  # exclude 'client'

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

class ClientForm(forms.Form):
    name = forms.CharField(label="New Client Name")
