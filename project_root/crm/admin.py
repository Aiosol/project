from django.contrib import admin
from .models import (
    CRMUser, 
    Customer, 
    OrderStatus, 
    # OrderNote,  # Commented out for now
    InventoryLog, 
    SalesTarget,
    Notification
)

@admin.register(CRMUser)
class CRMUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_per_page = 20

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer_type', 'lifetime_value', 'total_orders', 'last_purchase_date')
    list_filter = ('customer_type',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_per_page = 20

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_initial', 'is_processing', 'is_completed', 'is_cancelled', 'sort_order')
    list_filter = ('is_active', 'is_initial', 'is_processing', 'is_completed', 'is_cancelled')
    search_fields = ('name',)
    list_editable = ('sort_order',)
    list_per_page = 20

# @admin.register(OrderNote)
# class OrderNoteAdmin(admin.ModelAdmin):
#     list_display = ('order', 'user', 'created_at', 'is_customer_visible')
#     list_filter = ('is_customer_visible', 'created_at')
#     search_fields = ('note', 'order__id')
#     list_per_page = 20

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_change', 'action', 'performed_by', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('product__name', 'reason', 'notes')
    list_per_page = 20

@admin.register(SalesTarget)
class SalesTargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_amount', 'actual_amount', 'period', 'start_date', 'end_date', 'is_active')
    list_filter = ('period', 'is_active', 'start_date', 'end_date')
    search_fields = ('name',)
    list_per_page = 20

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'priority', 'is_read', 'created_at')
    list_filter = ('priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__user__username')
    list_per_page = 20