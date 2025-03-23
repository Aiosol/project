# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
]