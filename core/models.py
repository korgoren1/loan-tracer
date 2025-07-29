from django.db import models
from django.utils import timezone
from datetime import timedelta, date


class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class OpeningBalance(models.Model):
    date = models.DateField()
    amount = models.FloatField()

class Loan(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()
    date_issued = models.DateField(default=timezone.now)


    def days_remaining(self):
        due_date = self.date_issued + timedelta(days=12)
        return (due_date - date.today()).days
    
    def total_with_interest(self):
        return self.amount * 1.2

class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()
# core/models.py


TYPE_CHOICES = [
    ('saving', 'Saving'),
    ('drawing', 'Drawing'),
    ('expense', 'Expense'),
]

class MoneyOut(models.Model):
    amount = models.FloatField()
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True, default="")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.date} | {self.get_type_display()} | KES {self.amount} | {self.description}"


# Create your models here.
