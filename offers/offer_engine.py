# offers/offer_engine.py

#later we can do
#LAUNCH_OFFER_ENABLED = False

LAUNCH_OFFER_ENABLED = True

LAUNCH_OFFER = {
    "code": "B2G1",
    "title": "🎉 Buy 2 Get 1 Free",
    "description": "Buy 2 plants and get 1 cheaper plant free",
    "type": "BUY_TWO_GET_ONE",
}

def get_active_offer():
    if not LAUNCH_OFFER_ENABLED:
        return None
    return LAUNCH_OFFER

def apply_bogo(cart_items):
    """
    Buy 2 Get 1 Free
    Cheapest item free for every group of 3
    """
    prices = []

    for item in cart_items:
        prices.extend([item.product.price] * item.quantity)

    prices.sort()

    free_count = len(prices) // 3  # 🔥 BUY 2 GET 1
    discount = sum(prices[:free_count])

    return discount