# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from orders.admin import OrderAdminSite


# Create custom admin site
order_admin_site = OrderAdminSite(name='order_admin')

# Register models with custom admin site
from orders.models import Order, OrderItem
order_admin_site.register(Order)
order_admin_site.register(OrderItem)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),

    path('admin/', admin.site.urls),
    path('order-admin/', order_admin_site.urls),
    path('crm/', include('crm.urls', namespace='crm')),
]

# Add static and media URL patterns if not already done
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)