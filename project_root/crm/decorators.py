# crm/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps

def crm_login_required(view_func):
    """Simplified decorator for initial development"""
    @login_required(login_url='crm:login')
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # For initial development, just pass through
        return view_func(request, *args, **kwargs)
    return wrapper