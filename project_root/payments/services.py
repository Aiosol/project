# payments/services.py
import requests  # Make sure this is imported
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class BkashPaymentService:
    def __init__(self):
        self.app_key = settings.BKASH_APP_KEY
        self.app_secret = settings.BKASH_APP_SECRET
        self.username = settings.BKASH_USERNAME
        self.password = settings.BKASH_PASSWORD
        self.base_url = settings.BKASH_BASE_URL
        self.id_token = None
        
    def get_token(self):
        """Get an auth token from bKash"""
        url = f"{self.base_url}/tokenized/checkout/token/grant"
        
        headers = {
            "username": self.username,
            "password": self.password,
            "Content-Type": "application/json"
        }
        
        payload = {
            "app_key": self.app_key,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code != 200:
                print(f"bKash token error: {response.text}")
                return None
                
            data = response.json()
            self.id_token = data.get('id_token')
            return data
            
        except Exception as e:
            print(f"Error getting bKash token: {str(e)}")
            return None
    
    def create_payment(self, amount, invoice, callback_url):
        """Create a payment request"""
        token_response = self.get_token()
        if not token_response or not self.id_token:
            print("Failed to get authentication token")
            return {"success": False, "message": "Failed to get authentication token"}
        
        url = f"{self.base_url}/tokenized/checkout/create"
        
        headers = {
            "Authorization": self.id_token,
            "x-app-key": self.app_key,
            "Content-Type": "application/json"
        }
        
        # Format amount to 2 decimal places
        formatted_amount = "{:.2f}".format(float(amount))
        
        payload = {
            "mode": "0011",
            "payerReference": "01770618575",
            "callbackURL": callback_url,
            "amount": formatted_amount,
            "currency": "BDT",
            "intent": "sale",
            "merchantInvoiceNumber": invoice
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code != 200:
                print(f"bKash create payment error: {response.text}")
                return {"success": False, "message": f"Payment creation failed with status {response.status_code}"}
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"Error creating bKash payment: {str(e)}")
            return {"success": False, "message": f"Payment creation failed: {str(e)}"}
            
    def execute_payment(self, payment_id):
        """Execute a payment after user confirmation"""
        if not self.id_token:
            token_response = self.get_token()
            if not token_response or not self.id_token:
                return {"success": False, "message": "Failed to get authentication token"}
        
        url = f"{self.base_url}/tokenized/checkout/execute"
        
        headers = {
            "Authorization": self.id_token,
            "x-app-key": self.app_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "paymentID": payment_id
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code != 200:
                print(f"bKash execute payment error: {response.text}")
                return {"success": False, "message": f"Payment execution failed with status {response.status_code}"}
            
            return response.json()
            
        except Exception as e:
            print(f"Error executing bKash payment: {str(e)}")
            return {"success": False, "message": f"Payment execution failed: {str(e)}"}