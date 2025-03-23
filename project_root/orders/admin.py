# orders/admin.py - Updated version
from django.contrib import admin
from .models import Order, OrderItem  # Import your Order models
from crm.models import OrderStatus
from django.contrib.admin import AdminSite

class OrderAdminSite(AdminSite):
    site_header = 'Order Management'
    site_title = 'Order Admin'
    index_title = 'Order Administration'
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variant', 'quantity', 'price', 'total_price']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_amount', 'payment_method', 'created_at', 'get_status']
    list_filter = ['created_at', 'payment_method']
    search_fields = ['id', 'customer__user__email', 'customer__user__first_name', 'customer__user__last_name']
    readonly_fields = ['customer', 'shipping_address', 'billing_address', 'payment_method', 
                      'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    def get_status(self, obj):
        return obj.status.name if obj.status else "Not Set"
    get_status.short_description = 'Status'
    
    # Don't allow deletion of orders
    def has_delete_permission(self, request, obj=None):
        return False