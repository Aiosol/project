# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product, ProductVariant
from .models import Cart, CartItem

def cart_detail(request):
    """
    Display the contents of the user's shopping cart
    """
    cart = request.cart
    cart_items = cart.items.all()
    
    context = {
        'title': 'Your Shopping Cart',
        'cart': cart,
        'cart_items': cart_items
    }
    return render(request, 'cart/cart.html', context)

@require_POST
def add_to_cart(request, product_variant_id):
    """
    Add a product variant to the shopping cart
    """
    try:
        cart = request.cart
        
        # First try to get a product variant
        try:
            product_variant = ProductVariant.objects.get(id=product_variant_id)
        except ProductVariant.DoesNotExist:
            # If not found, try to get a product and use its first variant
            product = get_object_or_404(Product, id=product_variant_id)
            product_variant = ProductVariant.objects.filter(product=product).first()
            
            # If no variants exist, handle the error
            if not product_variant:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'No variants available for this product'
                    }, status=400)
                messages.error(request, 'No variants available for this product')
                return redirect('home')
        
        quantity = int(request.POST.get('quantity', 1))
        
        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=product_variant,
            defaults={'quantity': quantity}
        )
        
        # If the item already existed, update the quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Return JSON response for AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product_variant.product.name} added to your cart',
                'cart_total': cart.total_items
            })
        
        messages.success(request, f'{product_variant.product.name} added to your cart')
        return redirect('cart:cart_detail')
    
    except Exception as e:
        print(f"Error adding to cart: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error adding item to cart: {str(e)}'
            }, status=400)
        messages.error(request, f'Error adding item to cart: {str(e)}')
        return redirect('home')

@require_POST
def remove_from_cart(request, item_id):
    """
    Remove an item from the shopping cart
    """
    cart = request.cart
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product_variant.product.name
    cart_item.delete()
    
    # Return JSON response for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from your cart',
            'cart_total': cart.total_items
        })
    
    messages.success(request, f'{product_name} removed from your cart')
    return redirect('cart:cart_detail')

@require_POST
def update_cart(request):
    """
    Update the quantities of items in the shopping cart
    """
    cart = request.cart
    
    for key, value in request.POST.items():
        if key.startswith('quantity_'):
            item_id = int(key.split('_')[1])
            try:
                cart_item = CartItem.objects.get(id=item_id, cart=cart)
                quantity = int(value)
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    cart_item.delete()
            except (CartItem.DoesNotExist, ValueError):
                pass
    
    messages.success(request, 'Your cart has been updated')
    return redirect('cart:cart_detail')