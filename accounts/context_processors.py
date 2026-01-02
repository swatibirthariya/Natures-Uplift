from .models import CartItem
from .models import Cart
def auth_links(request):
    return {
        "SHOW_LOGIN": not request.user.is_authenticated,
        "SHOW_LOGOUT": request.user.is_authenticated,
    }



def cart_count(request):
    if not request.user.is_authenticated:
        return {"cart_count": 0}

    try:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.items.count() if cart else 0
    except Exception:
        count = 0

    return {"cart_count": count}