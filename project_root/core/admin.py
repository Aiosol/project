# core/admin.py - UPDATED VERSION
from django.contrib import admin
from django.utils.html import mark_safe
from .models import SiteConfiguration

class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'active')
    list_filter = ('category', 'active')
    search_fields = ('name', 'description', 'key', 'value')
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "No image"
    
    image_preview.short_description = 'Preview'

# Register your model
admin.site.register(SiteConfiguration, SiteConfigurationAdmin)

# Basic admin customization
admin.site.site_header = 'Bangladesh E-commerce Admin'
admin.site.site_title = 'E-commerce Portal'
admin.site.index_title = 'Management Dashboard'