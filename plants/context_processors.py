from accounts.models import Cart
from django.db.models import Sum

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            total = cart.items.aggregate(
                total=Sum('quantity')
            )['total']
            return {'cart_count': total or 0}
        return {'cart_count': 0}
    else:
        cart = request.session.get('cart', {})
        return {'cart_count': sum(cart.values())}