# crm/urls.py
from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.crm_login, name='login'),
    path('logout/', views.crm_logout, name='logout'),
    
    # API
    path('api/sales-data/', views.sales_data_api, name='sales_data_api'),
    
    # Order management
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/notes/', views.add_order_note, name='add_order_note'),
    
    # Customer management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # Inventory management
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/log/', views.inventory_log, name='inventory_log'),
    path('inventory/adjust/<int:product_id>/', views.adjust_inventory, name='adjust_inventory'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/customers/', views.customer_report, name='customer_report'),
    
    # Sales targets
    path('targets/', views.sales_targets, name='sales_targets'),
    path('targets/create/', views.create_sales_target, name='create_sales_target'),
    path('targets/<int:target_id>/edit/', views.edit_sales_target, name='edit_sales_target'),
    
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

    # Add these to urlpatterns in crm/urls.py
path('orders/create/', views.create_order, name='create_order'),
path('orders/create/add-item/', views.add_order_item, name='add_order_item'),
path('orders/create/remove-item/<int:item_id>/', views.remove_order_item, name='remove_order_item'),

path('api/product/<int:product_id>/variants/', views.product_variants_api, name='product_variants_api'),

]

  
