# crm/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import CRMUser

def crm_login_required(view_func):
    @login_required(login_url='crm:login')
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user has CRM access
        try:
            if not hasattr(request, 'crm_user') or not request.crm_user:
                # Try to get or create CRM user profile
                crm_user, created = CRMUser.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'role': 'staff',
                        'is_active': True
                    }
                )
                request.crm_user = crm_user
                
                # If staff is trying to access admin-only views
                if not request.crm_user.is_active:
                    messages.error(request, "Your CRM account is not active.")
                    return redirect('crm:login')
        except Exception as e:
            messages.error(request, "You don't have access to the CRM.")
            return redirect('crm:login')
            
        return view_func(request, *args, **kwargs)
    return wrapper