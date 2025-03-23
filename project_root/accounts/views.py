 # accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm, AddressForm
from .models import Address
from cart.models import Cart

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # If there's a session cart, associate it with the user
            session_id = request.session.get('cart_id')
            if session_id:
                Cart.objects.filter(session_id=session_id).update(user=user, session_id=None)
            
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # If there's a session cart, associate it with the user
                session_id = request.session.get('cart_id')
                if session_id:
                    session_cart = Cart.objects.filter(session_id=session_id).first()
                    user_cart = Cart.objects.filter(user=user, session_id=None).first()
                    
                    if session_cart and user_cart:
                        # Merge carts if both exist
                        for item in session_cart.items.all():
                            user_item, created = user_cart.items.get_or_create(
                                product_variant=item.product_variant,
                                defaults={'quantity': 0}
                            )
                            user_item.quantity += item.quantity
                            user_item.save()
                        session_cart.delete()
                    elif session_cart:
                        # Associate session cart with user
                        session_cart.user = user
                        session_cart.session_id = None
                        session_cart.save()
                
                messages.success(request, f"Welcome back, {user.first_name}!")
                
                # Redirect to next parameter or home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def address_list_view(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})

@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully.")
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/add_address.html', {'form': form})

@login_required
def edit_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'accounts/edit_address.html', {'form': form})

@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('accounts:address_list')

@login_required
def set_default_address(request, pk, address_type):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.address_type = address_type
    address.is_default = True
    address.save()
    messages.success(request, f"Default {address_type} address updated.")
    return redirect('accounts:address_list')