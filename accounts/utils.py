from .models import Cart, CartItem
import requests
from django.conf import settings

from .models import Cart, CartItem
from plants.models import Plant
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

def merge_cart_after_login(request, user):
    session_cart = request.session.get("cart")

    if not session_cart:
        return

    cart, _ = Cart.objects.get_or_create(user=user)

    for product_id, qty in session_cart.items():
        product = Plant.objects.get(id=product_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            item.quantity += qty
        else:
            item.quantity = qty

        item.save()

    del request.session["cart"]







def send_otp_email(email, otp):
    """
    Send OTP email as HTML using Django's EmailMessage.
    """
    subject = "Your OTP Code"
    body = f"""
    <h2>Hello,</h2>
    <p>Your OTP for password reset is: <strong>{otp}</strong></p>
    <p>This OTP is valid for <strong>5 minutes</strong> only.</p>
    """

    email_msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    email_msg.content_subtype = 'html'  # important for HTML

    email_msg.send(fail_silently=False)
    return True

def get_whatsapp_otp_link(phone, otp):
    # WhatsApp FREE method (no API, no DLT)
    return f"https://wa.me/91{phone}?text=Your%20OTP%20is%20{otp}"