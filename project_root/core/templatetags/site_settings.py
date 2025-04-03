# core/templatetags/site_settings.py
from django import template
from ..utils import get_site_config

register = template.Library()

@register.simple_tag
def site_setting(name, default=None):
    return get_site_config(name, default)