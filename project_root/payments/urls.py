# payments/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('bkash/initiate/', views.bkash_payment, name='bkash_payment'),
    path('bkash/callback/', views.bkash_callback, name='bkash_callback'),
    path('bkash/success/', views.payment_success, name='payment_success'),
    path('bkash/failure/', views.payment_failure, name='payment_failure'),
]