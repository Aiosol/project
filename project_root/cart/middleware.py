# cart/middleware.py
import uuid
from .models import Cart

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user, session_id=None)
            request.cart = cart
        else:
            session_id = request.session.get('cart_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                request.session['cart_id'] = session_id
            
            cart, created = Cart.objects.get_or_create(session_id=session_id)
            request.cart = cart
            
        response = self.get_response(request)
        return response