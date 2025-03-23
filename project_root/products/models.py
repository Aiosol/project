# products/models.py
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('simple', 'Simple Product'),
        ('variable', 'Variable Product')
    )
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # New field to determine if product has variants
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='simple')
    
    # Simple product specific fields - only used if product_type is 'simple'
    stock_quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def get_display_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def has_variants(self):
        return self.product_type == 'variable'
    
    @property
    def get_main_image(self):
        return self.images.first()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    is_main = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.product.name}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        variant_info = []
        if self.size:
            variant_info.append(f"Size: {self.size}")
        if self.color:
            variant_info.append(f"Color: {self.color}")
        
        return f"{self.product.name} ({', '.join(variant_info)})"
    
    @property
    def price(self):
        base_price = self.product.discount_price if self.product.discount_price else self.product.price
        return base_price + self.price_adjustment
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0