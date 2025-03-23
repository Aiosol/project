# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, ProductVariant

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = ProductVariant.objects.filter(product=product)
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'variants': variants,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def buy_now(request, product_id):
    """
    Direct purchase functionality - adds product to cart and redirects to checkout
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Get the default variant or first available variant
        variant = ProductVariant.objects.filter(product=product).first()
        if not variant:
            messages.error(request, "Sorry, this product is not available for purchase at the moment.")
            return redirect('products:product_detail', slug=product.slug)
        
        # Get user's cart
        cart = request.cart
        
        # Clear current cart items - buy now should only have this one product
        cart.items.all().delete()
        
        # Get quantity (default to 1 if not specified)
        quantity = int(request.POST.get('quantity', 1))
        
        # Add product to cart
        from cart.models import CartItem
        cart_item = CartItem.objects.create(
            cart=cart,
            product_variant=variant,
            quantity=quantity
        )
        
        # Redirect to checkout
        messages.success(request, f"{product.name} has been added to your cart. Proceed to checkout.")
        return redirect('orders:checkout')
        
    except Exception as e:
        messages.error(request, f"Error adding product to cart: {str(e)}")
        return redirect('home')