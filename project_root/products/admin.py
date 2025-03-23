# products/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant

# Simple inline classes
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0

# Basic product admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'category', 'product_type')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'discount_price', 'stock_quantity', 'sku')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
    )

# Simple category admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}

# Simple registration for other models
admin.site.register(ProductVariant)