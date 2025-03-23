# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('addresses/', views.address_list_view, name='address_list'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    path('addresses/edit/<int:pk>/', views.edit_address_view, name='edit_address'),
    path('addresses/delete/<int:pk>/', views.delete_address_view, name='delete_address'),
    path('addresses/set-default/<int:pk>/<str:address_type>/', views.set_default_address, name='set_default_address'),
]