from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import OrderStatus, CRMUser
from django.utils import timezone

class Command(BaseCommand):
    help = 'Sets up initial CRM data including order statuses and admin user'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up CRM data...')
        
        # Create default order statuses
        self.create_order_statuses()
        
        # Create admin user if not exists
        self.create_admin_user()
        
        self.stdout.write(self.style.SUCCESS('CRM setup completed successfully!'))
    
    def create_order_statuses(self):
        statuses = [
            {
                'name': 'Pending',
                'description': 'Order has been placed but not yet processed',
                'color_code': '#f6c23e',
                'is_active': True,
                'sort_order': 10,
                'is_initial': True,
                'is_processing': False,
                'is_completed': False,
                'is_cancelled': False
            },
            {
                'name': 'Processing',
                'description': 'Order is being processed',
                'color_code': '#4e73df',
                'is_active': True,
                'sort_order': 20,
                'is_initial': False,
                'is_processing': True,
                'is_completed': False,
                'is_cancelled': False
            },
            {
                'name': 'Shipped',
                'description': 'Order has been shipped',
                'color_code': '#1cc88a',
                'is_active': True,
                'sort_order': 30,
                'is_initial': False,
                'is_processing': True,
                'is_completed': False,
                'is_cancelled': False
            },
            {
                'name': 'Delivered',
                'description': 'Order has been delivered',
                'color_code': '#36b9cc',
                'is_active': True,
                'sort_order': 40,
                'is_initial': False,
                'is_processing': False,
                'is_completed': True,
                'is_cancelled': False
            },
            {
                'name': 'Cancelled',
                'description': 'Order has been cancelled',
                'color_code': '#e74a3b',
                'is_active': True,
                'sort_order': 50,
                'is_initial': False,
                'is_processing': False,
                'is_completed': False,
                'is_cancelled': True
            }
        ]
        
        for status_data in statuses:
            OrderStatus.objects.get_or_create(
                name=status_data['name'],
                defaults=status_data
            )
            
        self.stdout.write(f'Created {len(statuses)} order statuses')
    
    def create_admin_user(self):
        # Check if admin user exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write('Admin user already exists')
            return
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User'
        )
        
        # Create CRM user profile for admin
        CRMUser.objects.create(
            user=admin_user,
            role='admin',
            is_active=True,
            date_joined=timezone.now(),
            can_manage_orders=True,
            can_manage_inventory=True,
            can_view_reports=True,
            can_manage_customers=True
        )
        
        self.stdout.write('Created admin user with CRM profile')