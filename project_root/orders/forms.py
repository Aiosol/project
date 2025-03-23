# orders/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.Form):
    # Contact Information
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    
    # Address
    address_line_1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}))
    address_line_2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2 (Optional)'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}))
    
    # Payment
    payment_method = forms.ChoiceField(
        choices=[('cod', 'Cash on Delivery'), ('bkash', 'bKash Payment')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )