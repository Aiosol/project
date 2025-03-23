# orders/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import ProductVariant

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
    )
    
    # Order info
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Customer info
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Shipping info
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Payment info
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_id = models.CharField(max_length=100, blank=True) # For bKash transaction ID
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)
    
    # Totals
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Integration fields (for future API integration)
    # Steadfast Courier fields
    courier_tracking_code = models.CharField(max_length=20, blank=True, null=True)
    courier_consignment_id = models.CharField(max_length=20, blank=True, null=True)
    courier_status = models.CharField(max_length=30, blank=True, null=True)
    
    # Manager Accounting fields
    accounting_key = models.CharField(max_length=100, blank=True, null=True)
    accounting_reference = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Order {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)  # Store name in case product is deleted
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    @property
    def total_price(self):
        return self.price * self.quantity