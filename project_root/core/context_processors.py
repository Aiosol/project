# core/context_processors.py
from .utils import get_site_config

def site_settings(request):
    """Make common site settings available to all templates"""
    return {
        'site_name': get_site_config('site_name', 'Bangladesh E-commerce'),
        'site_logo': get_site_config('site_logo', '/static/img/default-logo.png'),
        'contact_email': get_site_config('contact_email', 'info@example.com'),
        'contact_phone': get_site_config('contact_phone', '+880xxxxxxxxx'),
    }