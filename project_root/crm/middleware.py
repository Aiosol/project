# crm/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import CRMUser

class CRMUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.crm_user = None
        if request.user.is_authenticated:
            try:
                request.crm_user = CRMUser.objects.get(user=request.user)
            except CRMUser.DoesNotExist:
                pass
        return None