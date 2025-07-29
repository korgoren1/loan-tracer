from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # Home
    path('search/', views.search_view, name='search'),
    path("daily-summary/", views.daily_summary_view, name="daily-summary"),
    path('client-summary/', views.client_summary_view, name='client-summary'),  # ✅ Add this
    path('client-summary/pdf/', views.client_summary_pdf, name='client-summary-pdf'),
    path('daily-summary/pdf/', views.daily_summary_pdf, name='daily-summary-pdf'),
    path('update-moneyout-description/', views.update_moneyout_description, name='update-moneyout-description'),


]
