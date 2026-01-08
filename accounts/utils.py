from .models import Cart, CartItem
from plants.models import Plant
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


# ==========================
# CART MERGE (UNCHANGED)
# ==========================
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


# ==========================
# BREVO EMAIL HELPER
# ==========================
def send_email_brevo(subject, html_content, to_emails):
    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": "Natures Uplift",
            "email": "no-reply@naturesuplift.com",
        },
        "to": [{"email": email} for email in to_emails],
        "subject": subject,
        "htmlContent": html_content,
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    if response.status_code >= 400:
        logger.error("❌ Brevo email failed: %s", response.text)
        return False

    return True


# ==========================
# OTP EMAIL (UPDATED → BREVO)
# ==========================
def send_otp_email(email, otp):
    """
    Send OTP email using Brevo (Render-safe).
    """
    subject = "Your OTP Code – Natures Uplift 🌱"
    body = f"""
    <h2>Hello,</h2>
    <p>Your OTP for password reset is:</p>
    <h3>{otp}</h3>
    <p>This OTP is valid for <strong>5 minutes</strong>.</p>
    <br>
    <p>Regards,<br><strong>Natures Uplift</strong></p>
    """

    return send_email_brevo(
        subject=subject,
        html_content=body,
        to_emails=[email],
    )


# ==========================
# WHATSAPP OTP (UNCHANGED)
# ==========================
def get_whatsapp_otp_link(phone, otp):
    return f"https://wa.me/91{phone}?text=Your%20OTP%20is%20{otp}"
