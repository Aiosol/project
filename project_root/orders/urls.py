# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('review/', views.order_review, name='review'),
    path('confirmation/<int:order_id>/', views.confirmation, name='confirmation'),
    path('history/', views.order_history, name='history'),
]