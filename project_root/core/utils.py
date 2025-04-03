# core/utils.py
from .models import SiteConfiguration

def get_site_config(name, default=None):
    """Fetch site configuration by name"""
    try:
        config = SiteConfiguration.objects.get(name=name, active=True)
        if config.value:
            return config.value
        elif config.image:
            return config.image.url
        return default
    except SiteConfiguration.DoesNotExist:
        return default