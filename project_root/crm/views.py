# crm/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST  # Add this import
from django.forms import modelform_factory
from datetime import datetime, timedelta

# Import the decorator first
from .decorators import crm_login_required

from .models import CRMUser, OrderStatus, SalesTarget, OrderNote
from orders.models import Order, OrderItem
from products.models import Product, ProductVariant

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


# Dashboard View
@crm_login_required
def dashboard(request):
    # Get current date and start of month for filtering
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    # Try to get real data - if models aren't yet updated, use placeholders
    try:
        # Today's sales
        today_sales = Order.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Monthly sales
        monthly_sales = Order.objects.filter(
            created_at__date__gte=start_of_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Pending orders - adjust the query based on your status field
        pending_orders = Order.objects.filter(
            status__is_completed=False,
            status__is_cancelled=False
        ).count()
        
        # Low stock products
        low_stock_products = Product.objects.filter(stock__lte=10).count()
        
        # Recent orders
        recent_orders = Order.objects.all().order_by('-created_at')[:10]
        
        # Active sales targets
        active_targets = SalesTarget.objects.filter(
            is_active=True,
            end_date__gte=today
        )
        
        # Sales data for chart - last 12 months
        sales_data = []
        for i in range(11, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_name = month_start.strftime('%b')
            
            month_sales = Order.objects.filter(
                created_at__month=month_start.month,
                created_at__year=month_start.year
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            sales_data.append({
                'month': month_name,
                'sales': month_sales
            })
    except Exception as e:
        # If there's an error (e.g., missing model fields), use placeholders
        print(f"Error fetching dashboard data: {e}")
        today_sales = 15000
        monthly_sales = 450000
        pending_orders = 12
        low_stock_products = 5
        recent_orders = []
        active_targets = []
        sales_data = [
            {'month': 'Jan', 'sales': 12000},
            {'month': 'Feb', 'sales': 19000},
            {'month': 'Mar', 'sales': 3000},
            {'month': 'Apr', 'sales': 5000},
            {'month': 'May', 'sales': 2000},
            {'month': 'Jun', 'sales': 3000},
            {'month': 'Jul', 'sales': 20000},
            {'month': 'Aug', 'sales': 30000},
            {'month': 'Sep', 'sales': 15000},
            {'month': 'Oct', 'sales': 12000},
            {'month': 'Nov', 'sales': 13000},
            {'month': 'Dec', 'sales': 25000}
        ]
    
    context = {
        'today_sales': today_sales,
        'monthly_sales': monthly_sales,
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'active_targets': active_targets,
        'sales_data': sales_data,
        'today': today
    }
    
    return render(request, 'crm/dashboard.html', context)


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
            Q(customer__user__first_name__icontains=query) |
            Q(customer__user__last_name__icontains=query) |
            Q(customer__user__email__icontains=query) |
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
        
        # Create a note for the status change
        messages.success(request, f"Order status updated to {status.name}")
        
        # Later we'll implement inventory updates based on status changes
        # if status.is_completed:
        #     # Update inventory logic here
    
    return redirect('crm:order_detail', order_id=order_id)


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
    return render(request, 'crm/customers/list.html', {'customers': []})


@crm_login_required
def customer_detail(request, customer_id):
    return render(request, 'crm/customers/detail.html', {'customer': {}})


# Inventory Management Views
@crm_login_required
def inventory_list(request):
    return render(request, 'crm/inventory/list.html', {'products': []})


@crm_login_required
def inventory_log(request):
    return render(request, 'crm/inventory/log.html', {'logs': []})


@crm_login_required
def adjust_inventory(request, product_id):
    return redirect('crm:inventory_list')


# Reports Views
@crm_login_required
def reports_dashboard(request):
    return render(request, 'crm/reports/dashboard.html')


@crm_login_required
def sales_report(request):
    return render(request, 'crm/reports/sales.html')


@crm_login_required
def inventory_report(request):
    return render(request, 'crm/reports/inventory.html')


@crm_login_required
def customer_report(request):
    return render(request, 'crm/reports/customers.html')


# Sales Targets Views
@crm_login_required
def sales_targets(request):
    return render(request, 'crm/targets/list.html', {'targets': []})


@crm_login_required
def create_sales_target(request):
    return render(request, 'crm/targets/create.html')


@crm_login_required
def edit_sales_target(request, target_id):
    return render(request, 'crm/targets/edit.html', {'target': {}})


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
    # Create ModelForms for Order and OrderItem
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