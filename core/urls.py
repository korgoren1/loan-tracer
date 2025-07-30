from django.urls import path
from . import views
from .views import data_entry_view
from .views import data_entry_view, delete_loan, delete_payment, delete_moneyout, delete_opening
from .views import edit_loan, edit_payment, edit_moneyout, edit_opening


urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # Home
    path('search/', views.search_view, name='search'),
    path("daily-summary/", views.daily_summary_view, name="daily-summary"),
    path('client-summary/', views.client_summary_view, name='client-summary'),  # ✅ Add this
    path('client-summary/pdf/', views.client_summary_pdf, name='client-summary-pdf'),
    path('daily-summary/pdf/', views.daily_summary_pdf, name='daily-summary-pdf'),
    path('update-moneyout-description/', views.update_moneyout_description, name='update-moneyout-description'),
    path('add-entry/', data_entry_view, name='data-entry'),
    path('add-entry/', data_entry_view, name='data_entry'),
    path('delete-loan/<int:pk>/', delete_loan, name='delete_loan'),
    path('delete-payment/<int:pk>/', delete_payment, name='delete_payment'),
    path('delete-moneyout/<int:pk>/', delete_moneyout, name='delete_moneyout'),
    path('delete-opening/<int:pk>/', delete_opening, name='delete_opening'),


    path('edit-loan/<int:pk>/', edit_loan, name='edit_loan'),
    path('edit-payment/<int:pk>/', edit_payment, name='edit_payment'),
    path('edit-moneyout/<int:pk>/', edit_moneyout, name='edit_moneyout'),
    path('edit-opening/<int:pk>/', edit_opening, name='edit_opening'),

]
