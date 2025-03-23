# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum, Count
from django.utils import timezone
import datetime

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'price', 'quantity', 'item_total')
    extra = 0
    
    def item_total(self, obj):
        return obj.price * obj.quantity
    item_total.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'phone', 'total_amount', 
                    'payment_method', 'status_colored', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_method', 'is_paid', 'created_at')
    search_fields = ('order_number', 'full_name', 'email', 'phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_paid']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'is_paid', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Shipping Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'postal_code')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_id', 'total_amount')
        }),
        ('Integration Information', {
            'fields': ('courier_tracking_code', 'courier_consignment_id', 'courier_status', 
                       'accounting_key', 'accounting_reference'),
            'classes': ('collapse',),
        }),
    )
    
    def customer_name(self, obj):
        return obj.full_name
    customer_name.short_description = 'Customer'
    
    def payment_status(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green; font-weight: bold;">Paid</span>')
        return format_html('<span style="color: red;">Unpaid</span>')
    payment_status.short_description = 'Payment'
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                           color, obj.get_status_display())
    status_colored.short_description = 'Status'
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "Mark selected orders as Processing"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    
    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
    mark_as_paid.short_description = "Mark selected orders as Paid"


class OrderAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('order-dashboard/', self.admin_view(self.order_dashboard), name='order_dashboard'),
        ]
        return custom_urls + urls
    
    def order_dashboard(self, request):
        # Get date ranges
        today = timezone.now().date()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        
        # Get statistics
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Today's orders
        today_orders = Order.objects.filter(created_at__date=today)
        today_count = today_orders.count()
        today_revenue = today_orders.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # This week's orders
        week_orders = Order.objects.filter(created_at__date__gte=start_of_week)
        week_count = week_orders.count()
        week_revenue = week_orders.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # This month's orders
        month_orders = Order.objects.filter(created_at__date__gte=start_of_month)
        month_count = month_orders.count()
        month_revenue = month_orders.filter(is_paid=True).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Status counts
        status_counts = Order.objects.values('status').annotate(count=Count('id'))
        status_data = {item['status']: item['count'] for item in status_counts}
        
        # Payment methods
        payment_methods = Order.objects.values('payment_method').annotate(count=Count('id'))
        payment_data = {item['payment_method']: item['count'] for item in payment_methods}
        
        # Recent orders
        recent_orders = Order.objects.order_by('-created_at')[:10]
        
        context = {
            'title': 'Order Dashboard',
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'today_count': today_count,
            'today_revenue': today_revenue,
            'week_count': week_count,
            'week_revenue': week_revenue,
            'month_count': month_count,
            'month_revenue': month_revenue,
            'status_data': status_data,
            'payment_data': payment_data,
            'recent_orders': recent_orders,
            'has_permission': True,
            'opts': Order._meta,
        }
        
        return TemplateResponse(request, 'admin/orders/order_dashboard.html', context)