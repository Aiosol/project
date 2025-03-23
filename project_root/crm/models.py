from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from products.models import Product  # Import your existing Product model
from accounts.models import User  # Import your existing User model

class CRMUser(models.Model):
    """CRM user roles and permissions"""
    ROLE_CHOICES = (
        ('admin', _('Admin')),
        ('manager', _('Manager')),
        ('staff', _('Staff')),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='crm_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Additional permissions
    can_manage_orders = models.BooleanField(default=False)
    can_manage_inventory = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_manage_customers = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

class Customer(models.Model):
    """Enhanced customer profile for CRM"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='crm_customer')
    
    # Customer classification
    CUSTOMER_TYPE_CHOICES = (
        ('regular', _('Regular')),
        ('vip', _('VIP')),
        ('wholesale', _('Wholesale')),
    )
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='regular')
    
    # Customer metrics
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    total_orders = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    
    # Customer communication
    email_opt_in = models.BooleanField(default=True)
    sms_opt_in = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_customer_type_display()})"

class OrderStatus(models.Model):
    """Order statuses for workflow management"""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default="#808080")  # Hex color code
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    
    # Status categories
    is_initial = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Order Statuses"
        ordering = ['sort_order']
    
    def __str__(self):
        return self.name

# Update crm/models.py to include OrderNote

class OrderNote(models.Model):
    """Internal notes for orders"""
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='crm_notes')
    user = models.ForeignKey(CRMUser, on_delete=models.SET_NULL, null=True, related_name='notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_customer_visible = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note on {self.order} by {self.user}"

class InventoryLog(models.Model):
    """Track inventory changes"""
    ACTION_CHOICES = (
        ('add', _('Added')),
        ('remove', _('Removed')),
        ('adjust', _('Adjustment')),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    quantity_change = models.IntegerField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    reason = models.CharField(max_length=100)
    performed_by = models.ForeignKey(CRMUser, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # Temporarily comment out Order reference
    # reference_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_action_display()} {abs(self.quantity_change)} of {self.product}"

class SalesTarget(models.Model):
    """Sales targets for performance tracking"""
    PERIOD_CHOICES = (
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('yearly', _('Yearly')),
    )
    
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_to = models.ForeignKey(CRMUser, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_period_display()})"
    
    def get_progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return round((self.actual_amount / self.target_amount) * 100, 2)

class Notification(models.Model):
    """System notifications for CRM users"""
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
    )
    
    recipient = models.ForeignKey(CRMUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title