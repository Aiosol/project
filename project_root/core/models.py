# core/models.py
from django.db import models
from django.core.files.storage import FileSystemStorage
import os

fs = FileSystemStorage(location='media/site_config/')

class SiteConfiguration(models.Model):
    """Site-wide settings controllable via admin"""
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # For storing images
    image = models.ImageField(upload_to='site_config/', blank=True, null=True)
    
    # For storing key-value settings
    key = models.CharField(max_length=50, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    
    # For ordering and organization
    category = models.CharField(max_length=50, default='general')
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configurations"
    
    def __str__(self):
        return self.name