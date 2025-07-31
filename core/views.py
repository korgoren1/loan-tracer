from django.shortcuts import render
from .models import Client, Loan, Payment
from django.db.models import Q
from datetime import datetime
from .models import OpeningBalance, MoneyOut
from django.db.models import Sum
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.db.models import Sum
from datetime import date
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import MoneyOut
from django.template.loader import render_to_string
from .utils import get_opening_balance
import weasyprint
from datetime import timedelta, date
from .models import Loan  # Ensure Loan is imported
from django import forms
from django.utils import timezone
from django.shortcuts import redirect
from .models import TYPE_CHOICES
from .models import OpeningBalance, Loan, Payment, MoneyOut
from .forms import LoanForm, PaymentForm, OpeningBalanceForm, MoneyOutForm,  ClientForm
from django.shortcuts import get_object_or_404
from .models import Client, Loan, Payment, MoneyOut, OpeningBalance




@require_POST
def update_moneyout_description(request):
    moneyout_id = request.POST.get("id")
    description = request.POST.get("description")

    try:
        entry = MoneyOut.objects.get(id=moneyout_id)
        entry.description = description
        entry.save()
        return JsonResponse({'success': True})
    except MoneyOut.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Entry not found'})

def search_view(request):
    query = request.GET.get("q", "")
    results = {}

    if query:
        results["clients"] = Client.objects.filter(name__icontains=query)
        results["loans"] = Loan.objects.filter(Q(client__name__icontains=query) | Q(date__icontains=query))
        results["payments"] = Payment.objects.filter(Q(client__name__icontains=query) | Q(date__icontains=query))

    return render(request, "core/search.html", {"results": results, "query": query})


def daily_summary_view(request):
    selected_date = request.GET.get("date", "")
    context = {"selected_date": selected_date}

    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

            opening = OpeningBalance.objects.filter(date=date_obj).first()
            opening_amount = opening.amount if opening else 0

            loans = Loan.objects.filter(date=date_obj)
            payments = Payment.objects.filter(date=date_obj)
            moneyouts = MoneyOut.objects.filter(date=date_obj)

            total_loans = sum([l.amount for l in loans])
            total_collections = sum([p.amount for p in payments])
            total_moneyout = sum([m.amount for m in moneyouts])

            closing_balance = opening_amount + total_collections - total_loans - total_moneyout

            today = timezone.localdate()
            tomorrow = today + timedelta(days=1)

            # ✅ Only auto-create if the selected date is today
            if date_obj == today:
                if not OpeningBalance.objects.filter(date=tomorrow).exists():
                    print("Creating tomorrow's opening balance...")
                    OpeningBalance.objects.create(date=tomorrow, amount=closing_balance)


            context.update({
                "opening": opening_amount,
                "total_loans": total_loans,
                "total_collections": total_collections,
                "total_moneyout": total_moneyout,
                "closing_balance": closing_balance,
                "loans": loans,
                "payments": payments,
                "moneyouts": moneyouts
            })

        except ValueError:
            context["error"] = "Invalid date format"

    return render(request, "core/daily_summary.html", context)


def client_summary_view(request):
    name_query = request.GET.get('name', '')

    clients = Client.objects.all()
    if name_query:
        clients = clients.filter(name__icontains=name_query)

    data = []

    for client in clients:
        loans = Loan.objects.filter(client=client)
        payments = Payment.objects.filter(client=client)

        total_loaned = loans.aggregate(Sum('amount'))['amount__sum'] or 0
        total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        total_interest = total_loaned * 0.2
        total_due = total_loaned + total_interest
        remaining = total_due - total_paid

        data.append({
            "client": client,
            "loans": loans,
            "payments": payments,
            "total_loaned": total_loaned,
            "total_paid": total_paid,
            "total_due": total_due,
            "remaining": remaining
        })

    return render(request, "core/client_summary.html", {
        "data": data,
        "name_query": name_query,
    })

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response

def client_summary_pdf(request):
    loans = Loan.objects.select_related("client")
    client_data = []

    for loan in loans:
        client = loan.client
        total_paid = sum(p.amount for p in Payment.objects.filter(client=client))
        total_due = loan.total_with_interest()
        remaining = total_due - total_paid
        daily_installment = round(total_due / 12, 2)

        client_data.append({
            "loan": loan,
            "client": client,
            "total_paid": total_paid,
            "remaining": remaining,
            "daily_installment": daily_installment,
        })

    context = {
        "client_data": client_data,
        "today": date.today(),
    }
    return render_to_pdf("core/client_summary_pdf.html", context)


def daily_summary_pdf(request):
    from datetime import datetime
    from .models import OpeningBalance, Loan, Payment, MoneyOut

    selected_date = request.GET.get("date")
    if not selected_date:
        return HttpResponse("Please provide a date in the URL: ?date=YYYY-MM-DD")

    try:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format")

    opening = OpeningBalance.objects.filter(date=date_obj).first()
    opening_amount = opening.amount if opening else 0

    loans = Loan.objects.filter(date=date_obj)
    payments = Payment.objects.filter(date=date_obj)
    moneyouts = MoneyOut.objects.filter(date=date_obj)

    total_loans = sum([l.amount for l in loans])
    total_collections = sum([p.amount for p in payments])
    total_moneyout = sum([m.amount for m in moneyouts])

    closing_balance = opening_amount + total_collections - total_loans - total_moneyout

    context = {
        "date": selected_date,
        "opening": opening_amount,
        "total_loans": total_loans,
        "total_collections": total_collections,
        "total_moneyout": total_moneyout,
        "closing_balance": closing_balance,
        "loans": loans,
        "payments": payments,
        "moneyouts": moneyouts,
    }

    template = get_template("core/daily_summary_pdf.html")
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    return response if not pisa_status.err else HttpResponse("PDF generation error")



def dashboard_view(request):
    name_query = request.GET.get("name", "")
    date_query = request.GET.get("date", "")

    loans = Loan.objects.all()
    payments = Payment.objects.all()

    if name_query:
        loans = loans.filter(client__name__icontains=name_query)
        payments = payments.filter(loan__client__name__icontains=name_query)

    if date_query:
        loans = loans.filter(date=date_query)
        payments = payments.filter(date=date_query)

    total_clients = Client.objects.count()
    total_loaned = loans.aggregate(Sum("amount"))["amount__sum"] or 0
    total_collected = payments.aggregate(Sum("amount"))["amount__sum"] or 0
    total_interest = total_loaned * 0.2
    total_due = total_loaned + total_interest
    total_remaining = total_due - total_collected

    # 🔽 New logic for today's closing balance
    today = timezone.localdate()
    opening = OpeningBalance.objects.filter(date=today).first()
    opening_amount = opening.amount if opening else 0

    today_loans = Loan.objects.filter(date=today)
    today_payments = Payment.objects.filter(date=today)
    today_moneyouts = MoneyOut.objects.filter(date=today)

    total_today_loans = sum([l.amount for l in today_loans])
    total_today_collections = sum([p.amount for p in today_payments])
    total_today_moneyout = sum([m.amount for m in today_moneyouts])

    closing_balance = opening_amount + total_today_collections - total_today_loans - total_today_moneyout

    # ✅ Now define context AFTER all calculations
    context = {
        "total_clients": total_clients,
        "total_loaned": total_loaned,
        "total_collected": total_collected,
        "total_remaining": total_remaining,
        "name_query": name_query,
        "date_query": date_query,
        "today": today,
        "closing_balance": closing_balance,
        "opening": opening_amount,
        "total_today_loans": total_today_loans,
        "total_today_collections": total_today_collections,
        "total_today_moneyout": total_today_moneyout,
    }

    return render(request, "core/dashboard.html", context)



def get_or_create_client(name):
    client, created = Client.objects.get_or_create(name__iexact=name.strip(), defaults={'name': name.strip()})
    return client


def data_entry_view(request):
    # Initialize blank forms
    loan_form = LoanForm()
    payment_form = PaymentForm()
    moneyout_form = MoneyOutForm()
    opening_form = OpeningBalanceForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # === Loan ===
        if form_type == 'loan':
            loan_form = LoanForm(request.POST)
            if loan_form.is_valid():
                client_name = loan_form.cleaned_data['client_name']
                client = get_or_create_client(client_name)

                Loan.objects.create(
                    client=client,
                    amount=loan_form.cleaned_data['amount'],
                    date=loan_form.cleaned_data['date'] or timezone.now().date()
                )
                return redirect('data_entry')

        # === Payment ===
        elif form_type == 'payment':
            payment_form = PaymentForm(request.POST)
            if payment_form.is_valid():
                client_name = payment_form.cleaned_data['client_name']
                client = get_or_create_client(client_name)

                Payment.objects.create(
                    client=client,
                    amount=payment_form.cleaned_data['amount'],
                    date=payment_form.cleaned_data['date'] or timezone.now().date()
                )
                return redirect('data_entry')

        # === Money Out ===
        elif form_type == 'moneyout':
            moneyout_form = MoneyOutForm(request.POST)
            if moneyout_form.is_valid():
                moneyout_form.save()
                return redirect('data_entry')

        # === Opening Balance ===
        elif form_type == 'opening':
            opening_form = OpeningBalanceForm(request.POST)
            if opening_form.is_valid():
                opening_form.save()
                return redirect('data_entry')

    # Load existing records
    context = {
        "loan_form": loan_form,
        "payment_form": payment_form,
        "moneyout_form": moneyout_form,
        "opening_form": opening_form,
        "loans": Loan.objects.all().order_by("-date"),
        "payments": Payment.objects.all().order_by("-date"),
        "moneyouts": MoneyOut.objects.all().order_by("-date"),
        "openings": OpeningBalance.objects.all().order_by("-date"),
    }
    return render(request, "core/data_entry.html", context)


def delete_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    loan.delete()
    return redirect('data_entry')

def delete_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.delete()
    return redirect('data_entry')

def delete_moneyout(request, pk):
    moneyout = get_object_or_404(MoneyOut, pk=pk)
    moneyout.delete()
    return redirect('data_entry')

def delete_opening(request, pk):
    opening = get_object_or_404(OpeningBalance, pk=pk)
    opening.delete()
    return redirect('data_entry')


def edit_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            return redirect('data-entry')  # or your preferred redirect
    else:
        form = LoanForm(instance=loan)
    return render(request, 'core/edit_form.html', {'form': form, 'title': 'Edit Loan'})

def edit_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('data-entry')  # or your preferred redirect
    else:
        form = PaymentForm(instance=payment)
    return render(request, 'core/edit_form.html', {'form': form, 'title': 'Edit Payment'})


def edit_moneyout(request, pk):
    moneyout = get_object_or_404(MoneyOut, pk=pk)
    form = MoneyOutForm(request.POST or None, instance=moneyout)
    if form.is_valid():
        form.save()
        return redirect('data_entry')
    return render(request, 'core/edit_form.html', {'form': form, 'title': 'Edit Money Out'})

def edit_opening(request, pk):
    opening = get_object_or_404(OpeningBalance, pk=pk)
    form = OpeningBalanceForm(request.POST or None, instance=opening)
    if form.is_valid():
        form.save()
        return redirect('data_entry')
    return render(request, 'core/edit_form.html', {'form': form, 'title': 'Edit Opening Balance'})
