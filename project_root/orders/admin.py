# orders/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Order, OrderItem
from products.models import Product, ProductVariant
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderAdminSite(AdminSite):
    site_header = 'Order Management'
    site_title = 'Order Admin'
    index_title = 'Order Administration'

# Create a custom admin site instance
order_admin = OrderAdminSite(name='order_admin')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Allow adding new items easily
    
    # Remove the autocomplete_fields line that's causing the error
    # autocomplete_fields = ['product', 'variant']
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.id:  # Only make fields readonly for existing orders
            return ['product', 'variant']
        return []

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_amount', 'payment_method', 'created_at', 'get_status']
    list_filter = ['created_at', 'payment_method', 'status']
    search_fields = ['id', 'customer__username', 'customer__email']
    readonly_fields = ['created_at', 'updated_at']  # Allow editing other fields
    inlines = [OrderItemInline]
    
    # Remove this line that's causing the error
    # autocomplete_fields = ['customer']
    
    def get_status(self, obj):
        return obj.status.name if obj.status and hasattr(obj.status, 'name') else "Not Set"
    get_status.short_description = 'Status'

# Register models with the default admin site
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)

# Register models with our custom admin site
order_admin.register(Order, OrderAdmin)
order_admin.register(OrderItem)

# Register the models that are referenced by autocomplete_fields
# This is optional - only needed if you want to keep autocomplete_fields
# admin.site.register(Product)
# admin.site.register(ProductVariant)
# admin.site.register(User)