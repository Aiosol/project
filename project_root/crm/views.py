# crm/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.forms import modelform_factory
from datetime import datetime, timedelta
import json
from django.http import HttpResponse, JsonResponse
import csv


from .forms import SalesTargetForm

# Import the decorator first
from .decorators import crm_login_required

from .models import CRMUser, OrderStatus, SalesTarget, OrderNote
from orders.models import Order, OrderItem
from products.models import Product, ProductVariant
from accounts.models import User 
from django.db import models
# Authentication Views
def crm_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                crm_user = CRMUser.objects.get(user=user, is_active=True)
                login(request, user)
                return redirect('crm:dashboard')
            except CRMUser.DoesNotExist:
                messages.error(request, "You don't have access to the CRM.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'crm/login.html')


def crm_logout(request):
    logout(request)
    return redirect('crm:login')


@crm_login_required
def dashboard(request):
    # Get current date and start of month for filtering
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    try:
        # TODAY'S SALES - Make sure this calculation is correct
        today_sales = Order.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # MONTHLY SALES
        monthly_sales = Order.objects.filter(
            created_at__date__gte=start_of_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # PENDING ORDERS - Make sure status field is properly used
        pending_orders = Order.objects.filter(
            status__is_initial=True  # Use proper status field relationship
        ).count()
        
        # LOW STOCK PRODUCTS
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=10
        ).count()
        
        # Recent orders with all needed relationships
        recent_orders = Order.objects.select_related(
            'customer', 'status'
        ).order_by('-created_at')[:10]
        
        # Active sales targets
        active_targets = SalesTarget.objects.filter(
            is_active=True,
            end_date__gte=today
        )
        
        # Sales chart data
        sales_data = []
        for i in range(11, -1, -1):
            month_date = today.replace(day=1) - timedelta(days=i*30)
            month_date = month_date.replace(day=1)  # Ensure first day of month
            month_name = month_date.strftime('%b')
            
            month_sales = Order.objects.filter(
                created_at__month=month_date.month,
                created_at__year=month_date.year
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            sales_data.append({
                'month': month_name,
                'sales': month_sales
            })
            
    except Exception as e:
        import traceback
        print(f"Dashboard error: {str(e)}")
        traceback.print_exc()
        # Fallback to placeholder data for graceful degradation
        today_sales = 0
        monthly_sales = 0
        pending_orders = 0
        low_stock_products = 0
        recent_orders = []
        active_targets = []
        sales_data = [{'month': m, 'sales': 0} for m in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
    
    # Get all status options for order update dropdowns
    statuses = OrderStatus.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'today_sales': today_sales,
        'monthly_sales': monthly_sales,
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'active_targets': active_targets,
        'sales_data': sales_data,
        'today': today,
        'statuses': statuses  # Don't forget this!
    }
    
    return render(request, 'crm/dashboard.html', context)


# Debug View to check OrderStatus records
@crm_login_required
def debug_view(request):
    order_statuses = OrderStatus.objects.all()
    orders = Order.objects.all()
    
    return JsonResponse({
        'status_count': order_statuses.count(),
        'statuses': list(order_statuses.values('id', 'name', 'is_initial', 'is_processing', 'is_completed')),
        'orders_count': orders.count(),
        'orders_with_status': Order.objects.filter(status__isnull=False).count(),
        'order_fields': [f.name for f in Order._meta.fields]
    })


# Sales Data API
def sales_data_api(request):
    period = request.GET.get('period', 'monthly')
    
    # Placeholder data for different periods
    if period == 'weekly':
        return JsonResponse({
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12'],
            'values': [5000, 7000, 10000, 8000, 12000, 15000, 11000, 9000, 8500, 14000, 16000, 19000]
        })
    elif period == 'yearly':
        return JsonResponse({
            'labels': ['2020', '2021', '2022', '2023', '2024'],
            'values': [120000, 180000, 240000, 300000, 360000]
        })
    else:  # Default to monthly
        return JsonResponse({
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'values': [12000, 19000, 3000, 5000, 2000, 3000, 20000, 30000, 15000, 12000, 13000, 25000]
        })

# Sales Targets Views
@crm_login_required
def sales_targets(request):
    """View for listing all sales targets"""
    # Get query parameters for filtering
    status = request.GET.get('status', 'active')  # Default to active targets
    
    # Get today's date
    today = timezone.now().date()
    
    try:
        # Start with all targets
        targets = SalesTarget.objects.all()
        
        # Apply filters
        if status == 'active':
            targets = targets.filter(is_active=True, end_date__gte=today)
        elif status == 'completed':
            targets = targets.filter(end_date__lt=today)
        elif status == 'archived':
            targets = targets.filter(is_active=False)
        
        # Order targets
        targets = targets.order_by('-start_date')
    except Exception as e:
        print(f"Error in sales_targets view: {str(e)}")
        import traceback
        traceback.print_exc()
        targets = SalesTarget.objects.none()  # Empty queryset
    
    context = {
        'targets': targets,
        'active_filter': status,
        'today': today  # Add today to context
    }
    
    return render(request, 'crm/targets/list.html', context)

@crm_login_required
def create_sales_target(request):
    """View for creating a new sales target"""
    try:
        if request.method == 'POST':
            # Create form instance with POST data
            form = SalesTargetForm(request.POST)
            
            if form.is_valid():
                # Save target and redirect
                target = form.save(commit=False)
                
                # Check if assigned_to is in the model
                if hasattr(SalesTarget, 'assigned_to') and hasattr(request, 'crm_user') and request.crm_user:
                    target.assigned_to = request.crm_user
                    
                target.save()
                messages.success(request, f"Sales target '{target.name}' created successfully")
                return redirect('crm:sales_targets')
            else:
                # Form has errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            # Create a blank form
            form = SalesTargetForm(initial={
                'start_date': timezone.now().date(),
                'end_date': (timezone.now().date() + timedelta(days=30)),
                'is_active': True,
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"Error creating sales target: {str(e)}")
        form = SalesTargetForm()  # Fallback to a blank form
    
    return render(request, 'crm/targets/create.html', {'form': form})

@crm_login_required
def edit_sales_target(request, target_id):
    """View for editing an existing sales target"""
    try:
        target = get_object_or_404(SalesTarget, id=target_id)
        
        if request.method == 'POST':
            form = SalesTargetForm(request.POST, instance=target)
            if form.is_valid():
                form.save()
                messages.success(request, f"Sales target '{target.name}' updated successfully")
                return redirect('crm:sales_targets')
        else:
            form = SalesTargetForm(instance=target)
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"Error editing sales target: {str(e)}")
        return redirect('crm:sales_targets')
    
    return render(request, 'crm/targets/edit.html', {
        'form': form, 
        'target': target
    })

@crm_login_required
def delete_sales_target(request, target_id):
    """View for deleting a sales target"""
    try:
        target = get_object_or_404(SalesTarget, id=target_id)
        
        if request.method == 'POST':
            target_name = target.name
            target.delete()
            messages.success(request, f"Sales target '{target_name}' deleted successfully")
            return redirect('crm:sales_targets')
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"Error deleting sales target: {str(e)}")
        return redirect('crm:sales_targets')
    
    return render(request, 'crm/targets/delete.html', {'target': target})
# Order Management Views
@crm_login_required
def order_list(request):
    # Get filter parameters
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    query = request.GET.get('q')
    
    # Start with all orders
    orders = Order.objects.all()
    
    # Apply filters
    if status:
        orders = orders.filter(status__id=status)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=date_to)
        except ValueError:
            pass
    
    if query:
        orders = orders.filter(
            Q(id__icontains=query) |
            Q(customer__username__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(customer__email__icontains=query) |
            Q(shipping_address__icontains=query)
        )
    
    # Handle export if requested
    if request.GET.get('export') == 'true':
        # We'll implement this later
        messages.info(request, "Export functionality will be implemented soon.")
    
    # Get order statuses for filter dropdown
    statuses = OrderStatus.objects.filter(is_active=True)
    
    context = {
        'orders': orders.order_by('-created_at'),
        'statuses': statuses,
        'filters': {
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
            'query': query
        }
    }
    
    return render(request, 'crm/orders/list.html', context)


@crm_login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    notes = OrderNote.objects.filter(order=order) if hasattr(order, 'crm_notes') else []
    statuses = OrderStatus.objects.filter(is_active=True)
    
    context = {
        'order': order,
        'notes': notes,
        'statuses': statuses
    }
    
    return render(request, 'crm/orders/detail.html', context)


@crm_login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        status_id = request.POST.get('status')
        status = get_object_or_404(OrderStatus, id=status_id)
        
        # Update the order status
        order.status = status
        order.save()
        
        # Add a message to confirm the update
        messages.success(request, f"Order #{order.id} status updated to {status.name}")
        
        # Redirect back to the referring page (could be dashboard or order detail)
        return redirect(request.META.get('HTTP_REFERER', 'crm:dashboard'))
    
    # If not a POST request, redirect to dashboard
    return redirect('crm:dashboard')


@crm_login_required
def add_order_note(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        note_text = request.POST.get('note')
        is_customer_visible = request.POST.get('is_customer_visible') == 'on'
        
        if note_text:
            OrderNote.objects.create(
                order=order,
                user=request.crm_user,
                note=note_text,
                is_customer_visible=is_customer_visible
            )
            
            messages.success(request, "Note added successfully")
        else:
            messages.error(request, "Note text cannot be empty")
    
    return redirect('crm:order_detail', order_id=order_id)


# Customer Management Views
@crm_login_required
def customer_list(request):
    """View for listing all customers with optional filtering"""
    # Get filter parameters
    customer_type = request.GET.get('customer_type', '')
    query = request.GET.get('q', '')
    show_type = request.GET.get('show', 'all')  # all, registered, guest
    
    from django.contrib.auth import get_user_model
    from orders.models import Order
    from .models import Customer
    from django.db.models import Count, Sum, Max, F, Value, CharField, Q
    from django.db.models.functions import Concat
    from django.utils import timezone
    
    User = get_user_model()
    
    # Prepare combined result list
    all_customers = []
    
    # PART 1: Get registered users (with or without orders)
    if show_type in ['all', 'registered']:
        registered_users = User.objects.annotate(
            total_orders=Count('orders', distinct=True),
            lifetime_value=Sum('orders__total_amount'),
            last_purchase_date=Max('orders__created_at')
        )
        
        # Apply search filters if any
        if query:
            registered_users = registered_users.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        
        # Process each registered user
        for user in registered_users:
            # Get or create CRM customer record
            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'customer_type': 'regular',
                    'total_orders': user.total_orders or 0,
                    'lifetime_value': user.lifetime_value or 0,
                    'last_purchase_date': user.last_purchase_date,
                    'email_opt_in': True,
                    'sms_opt_in': True
                }
            )
            
            # Always update to ensure data is current
            if not created:
                customer.total_orders = user.total_orders or 0
                customer.lifetime_value = user.lifetime_value or 0
                customer.last_purchase_date = user.last_purchase_date
                customer.save()
            
            # Skip if filtering by customer type and doesn't match
            if customer_type and customer.customer_type != customer_type:
                continue
                
            all_customers.append({
                'id': f"reg_{user.id}",  # Prefix to distinguish from guest customers
                'user': user,
                'customer': customer,
                'email': user.email,
                'name': user.get_full_name() or user.username,
                'total_orders': user.total_orders or 0,
                'lifetime_value': user.lifetime_value or 0,
                'last_purchase_date': user.last_purchase_date,
                'is_registered': True,
                'customer_type': customer.customer_type,
                'get_customer_type_display': customer.get_customer_type_display()
            })
    
    # PART 2: Get guest orders (grouped by shipping info)
    if show_type in ['all', 'guest']:
        # Find orders without associated user accounts
        guest_orders = Order.objects.filter(
            customer__isnull=True,
            shipping_address__isnull=False  # Ensure shipping address exists
        ).exclude(shipping_address='')
        
        # Apply search filter if any
        if query:
            guest_orders = guest_orders.filter(
                shipping_address__icontains=query
            )
        
        # Create a dictionary to group orders by similar shipping info
        guest_customers = {}
        
        for order in guest_orders:
            # Extract email from shipping address if possible
            import re
            email_match = re.search(r'Email: ([^\n]+)', order.shipping_address)
            name_match = re.search(r'^([^\n]+)', order.shipping_address)
            
            guest_email = email_match.group(1) if email_match else f"guest_{order.id}@example.com"
            guest_name = name_match.group(1) if name_match else f"Guest Customer"
            
            if guest_email not in guest_customers:
                guest_customers[guest_email] = {
                    'name': guest_name,
                    'email': guest_email,
                    'orders': [],
                    'total_orders': 0,
                    'lifetime_value': 0,
                    'last_purchase_date': None
                }
            
            guest_customers[guest_email]['orders'].append(order)
            guest_customers[guest_email]['total_orders'] += 1
            guest_customers[guest_email]['lifetime_value'] += order.total_amount or 0
            
            # Update last purchase date if needed
            if (not guest_customers[guest_email]['last_purchase_date'] or 
                (order.created_at and guest_customers[guest_email]['last_purchase_date'] < order.created_at)):
                guest_customers[guest_email]['last_purchase_date'] = order.created_at
        
        # Add guest customers to the result list
        for email, data in guest_customers.items():
            all_customers.append({
                'id': f"guest_{email}",  # Using email as identifier
                'user': None,
                'customer': None,  # No Customer model for guests
                'email': email,
                'name': data['name'],
                'total_orders': data['total_orders'],
                'lifetime_value': data['lifetime_value'],
                'last_purchase_date': data['last_purchase_date'],
                'is_registered': False,
                'customer_type': 'guest',
                'get_customer_type_display': 'Guest'
            })
    
    # Calculate status for each customer
    today = timezone.now().date()
    for customer in all_customers:
        if customer['last_purchase_date']:
            try:
                days_since = (today - customer['last_purchase_date'].date()).days
                if days_since <= 30:
                    customer['status'] = 'active'
                    customer['status_display'] = 'Active'
                    customer['status_color'] = 'success'
                elif days_since <= 90:
                    customer['status'] = 'at_risk'
                    customer['status_display'] = 'At Risk'
                    customer['status_color'] = 'warning'
                else:
                    customer['status'] = 'inactive'
                    customer['status_display'] = 'Inactive'
                    customer['status_color'] = 'danger'
            except (AttributeError, TypeError):
                # Handle any issues with date calculation
                customer['status'] = 'unknown'
                customer['status_display'] = 'Unknown'
                customer['status_color'] = 'secondary'
        else:
            customer['status'] = 'new'
            customer['status_display'] = 'New'
            customer['status_color'] = 'secondary'
    
    # Handle export functionality if requested
    if request.GET.get('export') == 'true':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Type', 'Orders', 'Lifetime Value', 'Last Purchase', 'Status'])
        
        for customer in all_customers:
            writer.writerow([
                customer['id'],
                customer['name'],
                customer['email'],
                customer['get_customer_type_display'],
                customer['total_orders'],
                customer['lifetime_value'],
                customer['last_purchase_date'].strftime('%Y-%m-%d') if customer['last_purchase_date'] else 'Never',
                customer['status_display']
            ])
        
        return response
    
    # Pass context data to template
    context = {
        'customers': all_customers,
        'filters': {
            'customer_type': customer_type,
            'query': query,
            'show_type': show_type
        }
    }
    
    return render(request, 'crm/customers/list.html', context)


@crm_login_required
def customer_detail(request, customer_id):
    """View for displaying detailed customer information - handles both registered and guest customers"""
    from .models import Customer
    from orders.models import Order
    from django.utils import timezone
    from datetime import timedelta
    from django.http import Http404
    
    # Parse customer_id to determine type (registered or guest)
    is_registered = customer_id.startswith('reg_')
    is_guest = customer_id.startswith('guest_')
    
    if is_registered:
        # Handle registered customer
        user_id = customer_id.replace('reg_', '')
        customer = get_object_or_404(Customer.objects.select_related('user'), user__id=user_id)
        user = customer.user
        
        # Get orders for this registered customer
        orders = Order.objects.filter(customer=user).select_related('status').order_by('-created_at')
        
        # Update customer metrics
        customer.total_orders = orders.count()
        customer.lifetime_value = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Update last purchase date if needed
        last_order = orders.first()
        if last_order:
            customer.last_purchase_date = last_order.created_at
            
        # Save updated metrics
        customer.save()
        
        email = user.email
        name = user.get_full_name() or user.username
        customer_type = customer.get_customer_type_display()
        
    elif is_guest:
        # Handle guest customer
        email = customer_id.replace('guest_', '')
        
        # Get orders for this guest customer based on email in shipping address
        orders = Order.objects.filter(
            customer__isnull=True,
            shipping_address__icontains=f"Email: {email}"
        ).select_related('status').order_by('-created_at')
        
        if not orders.exists():
            raise Http404("Guest customer not found")
            
        # Get the most recent order for name and other details
        latest_order = orders.first()
        
        # Extract name from shipping address
        import re
        name_match = re.search(r'^([^\n]+)', latest_order.shipping_address)
        name = name_match.group(1) if name_match else "Guest Customer"
        
        # Create a placeholder customer object with metrics
        from types import SimpleNamespace
        customer = SimpleNamespace(
            user=None,
            total_orders=orders.count(),
            lifetime_value=orders.aggregate(total=Sum('total_amount'))['total'] or 0,
            last_purchase_date=latest_order.created_at,
            customer_type='guest',
            get_customer_type_display=lambda: 'Guest',
            email_opt_in=False,
            sms_opt_in=False,
            notes="Guest customer (no account)"
        )
        customer_type = 'Guest'
    else:
        # Direct numeric ID (for backward compatibility)
        try:
            customer_id = int(customer_id)
            customer = get_object_or_404(Customer.objects.select_related('user'), id=customer_id)
            user = customer.user
            
            # Get orders for this registered customer
            orders = Order.objects.filter(customer=user).select_related('status').order_by('-created_at')
            
            # Update customer metrics
            customer.total_orders = orders.count()
            customer.lifetime_value = orders.aggregate(total=Sum('total_amount'))['total'] or 0
            
            # Update last purchase date if needed
            last_order = orders.first()
            if last_order:
                customer.last_purchase_date = last_order.created_at
                
            # Save updated metrics
            customer.save()
            
            email = user.email
            name = user.get_full_name() or user.username
            customer_type = customer.get_customer_type_display()
            is_registered = True
        except (ValueError, TypeError):
            raise Http404("Customer not found")
    
    # Calculate metrics (same for both types)
    total_spent = customer.lifetime_value
    total_orders = customer.total_orders
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0
    
    # Calculate days since first and last order
    first_order = orders.order_by('created_at').first()
    last_order = orders.order_by('-created_at').first()
    
    days_since_first_order = (timezone.now().date() - first_order.created_at.date()).days if first_order else 0
    days_since_last_order = (timezone.now().date() - last_order.created_at.date()).days if last_order else 999
    
    # Calculate purchase frequency (average days between orders)
    if total_orders > 1 and first_order and last_order:
        date_range = (last_order.created_at.date() - first_order.created_at.date()).days
        purchase_frequency = date_range / (total_orders - 1)
    else:
        purchase_frequency = 0
    
    # Pass context data to template
    context = {
        'customer': customer,
        'orders': orders,
        'total_spent': total_spent,
        'avg_order_value': avg_order_value,
        'days_since_last_order': days_since_last_order,
        'purchase_frequency': purchase_frequency,
        'is_registered': is_registered if 'is_registered' in locals() else True,
        'email': email,
        'name': name,
        'customer_type': customer_type
    }
    
    return render(request, 'crm/customers/detail.html', context)


@require_POST
@crm_login_required
def update_customer(request, customer_id):
    """Update customer details"""
    from .models import Customer
    
    # Only registered customers can be updated
    if not customer_id.startswith('reg_'):
        messages.error(request, "Cannot update guest customer")
        return redirect('crm:customer_list')
    
    user_id = customer_id.replace('reg_', '')
    customer = get_object_or_404(Customer, user__id=user_id)
    
    # Update customer fields from form data
    customer_type = request.POST.get('customer_type')
    email_opt_in = request.POST.get('email_opt_in') == 'on'
    sms_opt_in = request.POST.get('sms_opt_in') == 'on'
    notes = request.POST.get('notes', '')
    
    # Update the customer object
    customer.customer_type = customer_type
    customer.email_opt_in = email_opt_in
    customer.sms_opt_in = sms_opt_in
    customer.notes = notes
    customer.save()
    
    messages.success(request, "Customer details updated successfully")
    return redirect('crm:customer_detail', customer_id=customer_id)


# Inventory Management Views
@crm_login_required
def inventory_list(request):
    # Basic implementation
    products = Product.objects.all().order_by('-stock_quantity')[:50]
    return render(request, 'crm/inventory/list.html', {'products': products})


 


# Reports Views
@crm_login_required
def reports_dashboard(request):
    # Basic implementation
    return render(request, 'crm/reports/dashboard.html', {})

 



# User Management Views
@crm_login_required
def user_list(request):
    return render(request, 'crm/users/list.html', {'users': []})


@crm_login_required
def create_user(request):
    return render(request, 'crm/users/create.html')


@crm_login_required
def edit_user(request, user_id):
    return render(request, 'crm/users/edit.html', {'user': {}})


# Notification Views
@crm_login_required
def notification_list(request):
    return render(request, 'crm/notifications/list.html', {'notifications': []})


@crm_login_required
def mark_notification_read(request, notification_id):
    return redirect('crm:notification_list')


# Manual Order Creation Views
@crm_login_required
def create_order(request):
    """Create a new order manually"""
    OrderForm = modelform_factory(
        Order, 
        fields=['customer', 'shipping_address', 'billing_address', 'payment_method', 'payment_status', 'status']
    )
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create order but don't save yet
            order = form.save(commit=False)
            
            # Calculate total from session items
            items = request.session.get('manual_order_items', [])
            total = sum(item['price'] * item['quantity'] for item in items)
            order.total_amount = total
            
            # Save the order
            order.save()
            
            # Create order items
            for item_data in items:
                OrderItem.objects.create(
                    order=order,
                    product_id=item_data['product_id'],
                    variant_id=item_data.get('variant_id'),
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
            
            # Clear session data
            if 'manual_order_items' in request.session:
                del request.session['manual_order_items']
            
            messages.success(request, f"Order #{order.id} created successfully")
            return redirect('crm:order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    # Get items from session
    items = request.session.get('manual_order_items', [])
    item_details = []
    
    for item in items:
        product = Product.objects.get(id=item['product_id'])
        variant = ProductVariant.objects.get(id=item['variant_id']) if item.get('variant_id') else None
        
        item_details.append({
            'id': item.get('id', 0),
            'product': product,
            'variant': variant,
            'quantity': item['quantity'],
            'price': item['price'],
            'total': item['price'] * item['quantity']
        })
    
    # Calculate total
    total = sum(item['total'] for item in item_details)
    
    context = {
        'form': form,
        'items': item_details,
        'total': total,
        'products': Product.objects.all()
    }
    
    return render(request, 'crm/orders/create.html', context)


@require_POST
@crm_login_required
def add_order_item(request):
    """Add an item to the manual order"""
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id', None)
    quantity = int(request.POST.get('quantity', 1))
    
    # Get product and price
    product = get_object_or_404(Product, id=product_id)
    price = product.discount_price if product.discount_price else product.price
    
    # Get items from session or initialize empty list
    items = request.session.get('manual_order_items', [])
    
    # Add new item with unique id
    import time
    items.append({
        'id': int(time.time() * 1000),  # Use timestamp as id
        'product_id': int(product_id),
        'variant_id': int(variant_id) if variant_id else None,
        'quantity': quantity,
        'price': float(price)
    })
    
    # Save back to session
    request.session['manual_order_items'] = items
    
    return redirect('crm:create_order')


@crm_login_required
def remove_order_item(request, item_id):
    """Remove an item from the manual order"""
    items = request.session.get('manual_order_items', [])
    
    # Filter out the item with the given id
    items = [item for item in items if item.get('id') != item_id]
    
    # Save back to session
    request.session['manual_order_items'] = items
    
    return redirect('crm:create_order')


@crm_login_required
def product_variants_api(request, product_id):
    """API endpoint to get variants for a product"""
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)
    
    return JsonResponse({
        'variants': [
            {'id': variant.id, 'name': variant.name}
            for variant in variants
        ]
    })


@crm_login_required
def bulk_update_status(request):
    """Update status for multiple orders"""
    if request.method == 'POST':
        order_ids = request.POST.get('order_ids', '').split(',')
        status_id = request.POST.get('status')
        
        if order_ids and status_id:
            try:
                status = OrderStatus.objects.get(id=status_id)
                updated = Order.objects.filter(id__in=order_ids).update(status=status)
                messages.success(request, f"Updated status for {updated} orders to {status.name}")
            except OrderStatus.DoesNotExist:
                messages.error(request, "Invalid status selected")
        else:
            messages.error(request, "No orders or status selected")
            
    return redirect('crm:dashboard')

@crm_login_required
@require_POST
def bulk_delete_orders(request):
    """Delete multiple orders"""
    data = json.loads(request.body)
    order_ids = data.get('order_ids', [])
    
    if order_ids:
        deleted, _ = Order.objects.filter(id__in=order_ids).delete()
        if deleted > 0:
            return JsonResponse({'success': True, 'message': f"{deleted} orders deleted successfully"})
    
    return JsonResponse({'success': False, 'message': "Failed to delete orders"})

@crm_login_required
def export_orders(request):
    """Export selected orders as CSV"""
    order_ids = request.GET.get('ids', '').split(',')
    
    if not order_ids:
        messages.error(request, "No orders selected for export")
        return redirect('crm:dashboard')
    
    orders = Order.objects.filter(id__in=order_ids).select_related('customer', 'status')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Date', 'Customer', 'Total Amount', 'Status', 'Payment Method'])
    
    for order in orders:
        writer.writerow([
            order.id,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.customer.get_full_name() if order.customer else 'Guest',
            order.total_amount,
            order.status.name if order.status else 'Unknown',
            order.payment_method
        ])
    
    return response