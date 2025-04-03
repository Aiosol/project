# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CheckoutForm
from .models import Order, OrderItem
import uuid
from crm.models import OrderStatus

pending_status, created = OrderStatus.objects.get_or_create(
    name='Pending',
    defaults={
        'description': 'Order has been placed but not yet processed',
        'color_code': '#f6c23e',
        'is_active': True,
        'sort_order': 10,
        'is_initial': True,
        'is_processing': False,
        'is_completed': False,
        'is_cancelled': False
    }
)

def generate_order_number():
    # Generate a unique order number
    prefix = 'ORD'
    date_str = timezone.now().strftime('%y%m%d')
    random_str = str(uuid.uuid4().hex)[:6].upper()
    return f"{prefix}{date_str}{random_str}"

def checkout(request):
    """Checkout process - first step"""
    cart = request.cart
    
    # Check if cart is empty
    if cart.items.count() == 0:
        messages.warning(request, "Your cart is empty. Please add some products before checkout.")
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Store form data in session for review step
            request.session['checkout_data'] = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'address_line_1': form.cleaned_data['address_line_1'],
                'address_line_2': form.cleaned_data['address_line_2'],
                'city': form.cleaned_data['city'],
                'postal_code': form.cleaned_data['postal_code'],
                'shipping_location': form.cleaned_data['shipping_location'],
                'payment_method': form.cleaned_data['payment_method'],
            }
            
            # Proceed to review page
            return redirect('orders:review')
    else:
        # Pre-fill form with user information if logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'email': request.user.email,
            }
            
            # Add phone if user has profile
            if hasattr(request.user, 'profile') and request.user.profile.phone_number:
                initial_data['phone'] = request.user.profile.phone_number
                
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'orders/checkout.html', {
        'title': 'Checkout',
        'form': form,
        'cart': cart
    })

def order_review(request):
    """Review order before payment"""
    cart = request.cart
    
    # Check if cart is empty
    if cart.items.count() == 0:
        messages.warning(request, "Your cart is empty. Please add some products before checkout.")
        return redirect('cart:cart_detail')
    
    # Check if checkout data exists in session
    if 'checkout_data' not in request.session:
        messages.warning(request, "Please complete the checkout form first.")
        return redirect('orders:checkout')
    
    checkout_data = request.session['checkout_data']
    
    # Calculate shipping cost based on location
    shipping_location = checkout_data.get('shipping_location', 'inside_dhaka')
    shipping_cost = 120 if shipping_location == 'outside_dhaka' else 70
    
    # Calculate total with shipping
    total_with_shipping = float(cart.total_price) + shipping_cost

    if request.method == 'POST':
        # Get or create a "Pending" status
        from crm.models import OrderStatus
        pending_status, created = OrderStatus.objects.get_or_create(
            name='Pending',
            defaults={
                'description': 'Order has been placed but not yet processed',
                'color_code': '#f6c23e',
                'is_active': True,
                'sort_order': 10,
                'is_initial': True,
                'is_processing': False,
                'is_completed': False,
                'is_cancelled': False
            }
        )
        
        # Create the order with the new field structure
        order = Order(
            customer=request.user if request.user.is_authenticated else None,
            shipping_address=f"{checkout_data['full_name']}\n{checkout_data['address_line_1']}\n{checkout_data.get('address_line_2', '')}\n{checkout_data['city']}, {checkout_data['postal_code']}\nPhone: {checkout_data['phone']}\nEmail: {checkout_data['email']}",
            billing_address=None,  # Or set to shipping_address if needed
            payment_method=checkout_data['payment_method'],
            payment_status='pending',
            total_amount=total_with_shipping,  # Update this line
            status=pending_status
        )
        order.save()
        
        # Create order items
        for cart_item in cart.items.all():
            product_variant = cart_item.product_variant
            product = product_variant.product
            OrderItem.objects.create(
                order=order,
                product=product,
                variant=product_variant,
                quantity=cart_item.quantity,
                price=product.discount_price if product.discount_price else product.price
            )
        
        # Store order ID in session
        request.session['order_id'] = order.id
        
        # Process payment based on method
        if checkout_data['payment_method'] == 'cod':
            # For Cash on Delivery, clear cart and show confirmation
            cart.items.all().delete()
            
            # Clear checkout data
            if 'checkout_data' in request.session:
                del request.session['checkout_data']
                
            return redirect('orders:confirmation', order_id=order.id)
        elif checkout_data['payment_method'] == 'bkash':
            # For clearer debugging, let's print some info
            print(f"Redirecting to bKash payment for order {order.id}")
            print(f"Order ID in session: {request.session.get('order_id')}")
            
            # Redirect to bKash payment page
            return redirect('payments:bkash_payment')
        else:
            # Handle any unexpected payment methods
            messages.error(request, f"Unsupported payment method: {checkout_data['payment_method']}")
            return redirect('orders:checkout')
    
    return render(request, 'orders/review.html', {
        'title': 'Review Your Order',
        'cart': cart,
        'checkout_data': checkout_data,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total_with_shipping  # Add this line
    })

def confirmation(request, order_id):
    """Order confirmation page"""
    try:
        order = Order.objects.get(id=order_id)
        
        # Security check - only allow viewing by the order owner or if just placed (in session)
        session_order_id = request.session.get('order_id')
        if (request.user.is_authenticated and order.customer == request.user) or str(order.id) == str(session_order_id):
            # Clear the session order ID
            if 'order_id' in request.session:
                del request.session['order_id']
                
            return render(request, 'orders/confirmation.html', {
                'title': 'Order Confirmed',
                'order': order
            })
        else:
            messages.error(request, "You don't have permission to view this order.")
            return redirect('home')
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('home')

@login_required
def order_history(request):
    """User order history"""
    # Change this line from 'user=request.user' to 'customer=request.user'
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {
        'title': 'Order History',
        'orders': orders
    })