# cart/models.py
from django.db import models
from django.conf import settings
from products.models import ProductVariant, Product

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.id}"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product_variant')
    
    def __str__(self):
        return f"{self.quantity} x {self.product_variant}"
    
    @property
    def total_price(self):
        # Use the product's price if variant doesn't have a price
        if hasattr(self.product_variant, 'price'):
            variant_price = self.product_variant.price
        else:
            variant_price = self.product_variant.product.price
        return variant_price * self.quantity