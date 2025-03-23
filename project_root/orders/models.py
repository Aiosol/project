# orders/models.py - Key part to update
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User  # Adjust this import to match your project
from products.models import Product, ProductVariant  # Adjust this import to match your project

class Order(models.Model):
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add the status field with a default value
    status = models.ForeignKey('crm.OrderStatus', on_delete=models.SET_NULL, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    inventory_updated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Update in the orders/models.py file

# In orders/models.py - Update the total_price property
@property
def total_price(self):
    if self.price is None:
        return 0
    return self.price * self.quantity