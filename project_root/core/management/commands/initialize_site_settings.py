# core/management/commands/initialize_site_settings.py
from django.core.management.base import BaseCommand
from core.models import SiteConfiguration

class Command(BaseCommand):
    help = 'Initialize default site settings'

    def handle(self, *args, **kwargs):
        # Create default settings
        defaults = [
            {'name': 'site_name', 'value': 'Bangladesh E-commerce', 'category': 'general'},
            {'name': 'site_logo', 'category': 'design', 'description': 'Main site logo'},
            {'name': 'hero_banner', 'category': 'design', 'description': 'Homepage hero banner'},
            {'name': 'primary_color', 'value': '#4e73df', 'category': 'design'},
            {'name': 'footer_text', 'value': '© 2025 Bangladesh E-commerce. All rights reserved.', 'category': 'general'},
        ]
        
        for setting in defaults:
            SiteConfiguration.objects.get_or_create(
                name=setting['name'],
                defaults=setting
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully initialized site settings'))