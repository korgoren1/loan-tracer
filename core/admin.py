from django.contrib import admin
from .models import Client, Loan, Payment, MoneyOut, OpeningBalance

admin.site.register(Client)
admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(MoneyOut)
admin.site.register(OpeningBalance)

# Register your models here.
