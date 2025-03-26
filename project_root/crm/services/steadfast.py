# crm/services/steadfast.py

import requests
import logging
import json

logger = logging.getLogger(__name__)

class SteadfastCourier:
    """Service class for Steadfast Courier API integration"""
    
    BASE_URL = 'https://portal.packzy.com/api/v1'
    API_KEY = 'lvbzordcng9xvhx1rkc7gw3gjxngyzzw'
    SECRET_KEY = 'wtljzusnzyeditpwhnwthxky'
    
    def __init__(self):
        self.headers = {
            'Api-Key': self.API_KEY,
            'Secret-Key': self.SECRET_KEY,
            'Content-Type': 'application/json'
        }
    
    def create_order(self, invoice, recipient_name, recipient_phone, recipient_address, cod_amount, note=None):
        """Create a new delivery order in Steadfast"""
        url = f"{self.BASE_URL}/create_order"
        
        payload = {
            'invoice': invoice,
            'recipient_name': recipient_name,
            'recipient_phone': recipient_phone,
            'recipient_address': recipient_address,
            'cod_amount': float(cod_amount)
        }
        
        if note:
            payload['note'] = note
            
        try:
            logger.info(f"Sending order to Steadfast: {payload}")
            response = requests.post(url, headers=self.headers, json=payload)
            
            # Log the raw response for debugging
            logger.info(f"Steadfast response: {response.status_code} - {response.text}")
            
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return {'status': 'error', 'message': 'Invalid JSON response'}
        except Exception as e:
            logger.error(f"Error creating Steadfast order: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_bulk_orders(self, orders_data):
        """Create multiple delivery orders at once"""
        url = f"{self.BASE_URL}/create_order/bulk-order"
        
        payload = {
            'data': orders_data
        }
        
        try:
            logger.info(f"Sending bulk orders to Steadfast: {len(orders_data)} orders")
            # Log the first order as a sample (avoid logging everything)
            if orders_data:
                logger.info(f"Sample order data: {orders_data[0]}")
                
            response = requests.post(url, headers=self.headers, json=payload)
            
            # Log the raw response for debugging
            logger.info(f"Steadfast bulk response: {response.status_code} - {response.text[:500]}")
            
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return {'status': 'error', 'message': 'Invalid JSON response'}
        except Exception as e:
            logger.error(f"Error creating bulk Steadfast orders: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def check_status_by_invoice(self, invoice):
        """Check delivery status by invoice ID"""
        url = f"{self.BASE_URL}/status_by_invoice/{invoice}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            # Log the raw response for debugging
            logger.info(f"Steadfast status response: {response.status_code} - {response.text}")
            
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return {'status': 'error', 'message': 'Invalid JSON response'}
        except Exception as e:
            logger.error(f"Error checking status by invoice: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def check_status_by_tracking(self, tracking_code):
        """Check delivery status by tracking code"""
        url = f"{self.BASE_URL}/status_by_trackingcode/{tracking_code}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            # Log the raw response for debugging
            logger.info(f"Steadfast tracking response: {response.status_code} - {response.text}")
            
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return {'status': 'error', 'message': 'Invalid JSON response'}
        except Exception as e:
            logger.error(f"Error checking status by tracking: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_balance(self):
        """Check current account balance"""
        url = f"{self.BASE_URL}/get_balance"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return {'status': 'error', 'message': 'Invalid JSON response'}
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return {'status': 'error', 'message': str(e)}