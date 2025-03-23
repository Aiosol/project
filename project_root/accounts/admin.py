# accounts/admin.py
from django.contrib import admin
from .models import Profile, Address

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'birth_date']
    search_fields = ['user__username', 'user__email', 'phone_number']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'address_type', 'is_default', 'city']
    list_filter = ['address_type', 'is_default', 'city']
    search_fields = ['full_name', 'address_line_1', 'city', 'postal_code']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Address, AddressAdmin)