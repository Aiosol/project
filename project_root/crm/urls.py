# crm/urls.py
from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('login/', views.crm_login, name='login'),

    path('orders/', views.order_list, name='order_list'),
     
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
     
    path('users/', views.user_list, name='user_management'),
    path('logout/', views.crm_logout, name='logout'),
    
    # API
    path('api/sales-data/', views.sales_data_api, name='sales_data_api'),
    
    # Order management
     
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/notes/', views.add_order_note, name='add_order_note'),
    
     
     
  # Customer management
path('customers/', views.customer_list, name='customer_list'),
path('customers/<str:customer_id>/', views.customer_detail, name='customer_detail'),
path('customers/<str:customer_id>/update/', views.update_customer, name='update_customer'),
 
    
    # Inventory management
     
     
     
    
    # Reports
     
    
    
    # Sales targets
    # Add this to crm/urls.py
path('targets/', views.sales_targets, name='sales_targets'),
path('targets/create/', views.create_sales_target, name='create_sales_target'),
path('targets/<int:target_id>/edit/', views.edit_sales_target, name='edit_sales_target'),
path('targets/<int:target_id>/delete/', views.delete_sales_target, name='delete_sales_target'),
     
    
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
path('debug/', views.debug_view, name='debug'),


 
# Bulk actions
path('orders/bulk-status/', views.bulk_update_status, name='bulk_update_status'),
path('orders/bulk-delete/', views.bulk_delete_orders, name='bulk_delete_orders'),
path('orders/export/', views.export_orders, name='export_orders'),

# Add these to urlpatterns in crm/urls.py
path('orders/<int:order_id>/ship/', views.ship_order, name='ship_order'),
path('orders/<int:order_id>/status/check/', views.check_delivery_status, name='check_delivery_status'),
path('orders/bulk-ship/', views.bulk_ship_orders, name='bulk_ship_orders'),
path('shipping/queue/', views.shipping_queue, name='shipping_queue'),

]

  
