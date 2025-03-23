# orders/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from products.models import Product, ProductVariant

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)  # Made nullable
    billing_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)  # Made nullable
    payment_status = models.CharField(max_length=50, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Made nullable
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.ForeignKey('crm.OrderStatus', on_delete=models.SET_NULL, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    inventory_updated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)  # Made nullable
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True, default=1)  # Made nullable
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Made nullable
    
    @property
    def total_price(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity
    
    def __str__(self):
        product_name = self.product.name if self.product else "Unknown Product"
        return f"{self.quantity or 0} x {product_name}"