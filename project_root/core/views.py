
# core/views.py
from django.shortcuts import render
from products.models import Product, Category

def home(request):
    featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:8]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)