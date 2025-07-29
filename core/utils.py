# core/utils.py

from .models import OpeningBalance

def get_opening_balance(date):
    entry = OpeningBalance.objects.filter(date=date).first()
    return entry.amount if entry else 0
