from .models import Cart, CartItem
from plants.models import Plant
from django.conf import settings
import requests
import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings

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

def send_brevo_email(subject, html_content, to_email, to_name="User"):
    try:
        if not settings.BREVO_API_KEY:
            raise Exception("BREVO_API_KEY is missing")

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key = {
            'api-key': settings.BREVO_API_KEY
        }

        api_client = sib_api_v3_sdk.ApiClient(configuration)
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

        email = sib_api_v3_sdk.SendSmtpEmail(
            sender={
                "name": "natures uplift",
                "email": "no-reply@naturesuplift.com"
            },
            to=[{
                "email": to_email,
                "name": to_name
            }],
            subject=subject,
            html_content=html_content,
        )

        api_instance.send_transac_email(email)

    except ApiException as e:
        print("❌ Brevo API error:", e)
    except Exception as e:
        print("❌ Brevo setup error:", e)


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

    return send_brevo_email(
        subject=subject,
        html_content=body,
        to_emails=[email],
    )


# ==========================
# WHATSAPP OTP (UNCHANGED)
# ==========================
def get_whatsapp_otp_link(phone, otp):
    return f"https://wa.me/91{phone}?text=Your%20OTP%20is%20{otp}"
