# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
import json

from orders.models import Order
from .services import BkashPaymentService

def bkash_payment(request):
    """Initiate bKash payment"""
    # Get order from session
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "No order found. Please try again.")
        return redirect('cart:cart_detail')
    
    order = get_object_or_404(Order, id=order_id)
    print(f"Processing bKash payment for order {order.id}, amount {order.total_amount}")
    
    # Generate callback URL
    callback_url = request.build_absolute_uri(reverse('payments:bkash_callback'))
    print(f"Callback URL: {callback_url}")
    
    try:
        # Create bKash payment
        bkash_service = BkashPaymentService()
        response = bkash_service.create_payment(
            amount=float(order.total_amount),
            invoice=str(order.order_number),
            callback_url=callback_url
        )
        
        print(f"bKash API response: {response}")
        
        if 'bkashURL' in response:
            # Store payment ID in session
            request.session['payment_id'] = response['paymentID']
            
            # Redirect to bKash payment page
            print(f"Redirecting to: {response['bkashURL']}")
            return redirect(response['bkashURL'])
        else:
            # Payment creation failed
            error_message = "Failed to create payment. Please try again."
            if 'message' in response:
                error_message += f" Error: {response['message']}"
                
            messages.error(request, error_message)
            return redirect('orders:review')
    except Exception as e:
        print(f"Exception during bKash payment: {str(e)}")
        messages.error(request, f"Payment system error: {str(e)}")
        return redirect('orders:review')

@csrf_exempt
def bkash_callback(request):
    """Handle callback from bKash"""
    # Get payment ID and status from request
    payment_id = request.GET.get('paymentID')
    status = request.GET.get('status')
    
    print(f"bKash callback received: paymentID={payment_id}, status={status}")
    
    if not payment_id:
        messages.error(request, "Invalid payment information.")
        return redirect('cart:cart_detail')
    
    # Verify payment ID matches session
    session_payment_id = request.session.get('payment_id')
    if session_payment_id != payment_id:
        messages.error(request, "Payment validation failed.")
        return redirect('cart:cart_detail')
    
    # Get order from session
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "No order found. Please try again.")
        return redirect('cart:cart_detail')
    
    order = get_object_or_404(Order, id=order_id)
    
    if status == 'success':
        # Execute payment
        bkash_service = BkashPaymentService()
        response = bkash_service.execute_payment(payment_id)
        
        if 'trxID' in response:
            # Update order with payment info
            order.payment_id = response['trxID']
            order.is_paid = True
            order.status = 'processing'
            order.save()
            
            # Clear cart after successful payment
            request.cart.items.all().delete()
            
            # Clear session data
            if 'payment_id' in request.session:
                del request.session['payment_id']
            if 'checkout_data' in request.session:
                del request.session['checkout_data']
            
            messages.success(request, "Payment successful! Your order has been confirmed.")
            return redirect('orders:confirmation', order_id=order.id)
        else:
            messages.error(request, "Payment execution failed. Please contact support.")
    else:
        messages.error(request, "Payment was not completed. Please try again.")
    
    return redirect('orders:checkout')

def payment_success(request):
    """Payment success page"""
    return render(request, 'payments/success.html', {'title': 'Payment Successful'})

def payment_failure(request):
    """Payment failure page"""
    return render(request, 'payments/failure.html', {'title': 'Payment Failed'})