from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction

from .models import Payment
from accounts.models import Order, CartItem

import threading
import logging

# Brevo imports
from sib_api_v3_sdk import Configuration, ApiClient
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)

UPI_ID = "6366382516@ybl"


# ==============================
# BREVO EMAIL HELPER
# ==============================
def send_brevo_email(subject, html_content, to_email, to_name="User"):
    try:
        if not settings.BREVO_API_KEY:
            raise Exception("BREVO_API_KEY is missing")

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key = {
            'api-key': settings.BREVO_API_KEY  # 🔥 THIS IS CRITICAL
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
        print("✅ Brevo email sent to:", to_email)

    except ApiException as e:
        print("❌ Brevo API error:", e)
    except Exception as e:
        print("❌ Brevo setup error:", e)


# ==============================
# SEND ORDER EMAILS
# ==============================
def _send_order_emails(order):
    user = order.user
    items = order.items.all()
    payment = Payment.objects.filter(order=order).first()

    # --------------------
    # CUSTOMER EMAIL
    # --------------------
    if user.email:
        html_content = render_to_string(
            "emails/customer_order_email.html",
            {
                "order": order,
                "user": user,
            }
        )

        send_brevo_email(
            subject="Your order with Natures Uplift 🌱",
            html_content=html_content,
            to_email=user.email,
        )

    # --------------------
    # ADMIN EMAIL
    # --------------------
    html_content = render_to_string(
        "emails/admin_order_email.html",
        {
            "order": order,
            "items": items,
            "payment": payment
        }
    )

    send_brevo_email(
        subject="New Order Received – Natures Uplift 🌱",
        html_content=html_content,
        to_email=settings.ADMIN_EMAIL[0],
    )


def send_order_emails_async(order):
    threading.Thread(
        target=_send_order_emails,
        args=(order,),
        daemon=True
    ).start()


# ==============================
# START PAYMENT (UPI)
# ==============================
@login_required
def start_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    payment, _ = Payment.objects.get_or_create(
        order=order,
        defaults={
            "user": request.user,
            "amount": order.total_amount,
        },
    )

    gpay_link = (
        "tez://upi/pay"
        f"?pa={UPI_ID}"
        "&pn=NaturesUplift"
        f"&am={order.total_amount}"
        "&cu=INR"
    )

    phonepe_link = (
        "phonepe://pay"
        f"?pa={UPI_ID}"
        "&pn=NaturesUplift"
        f"&am={order.total_amount}"
        "&cu=INR"
    )

    return render(
        request,
        "payments/upi_payment.html",
        {
            "order": order,
            "payment": payment,
            "gpay_link": gpay_link,
            "phonepe_link": phonepe_link,
        },
    )


# ==============================
# SUBMIT UTR (UPI)
# ==============================
@login_required
def submit_utr(request, order_id):
    payment = get_object_or_404(Payment, order_id=order_id, user=request.user)
    order = payment.order

    if request.method == "POST":
        utr = request.POST.get("utr")

        if not utr:
            messages.error(request, "Please enter payment reference")
            return redirect("start_payment", order_id=order_id)

        with transaction.atomic():
            payment.utr_number = utr
            payment.status = "UNDER_REVIEW"
            payment.save()

            order.payment_method = "UPI"
            order.status = "PENDING"
            order.save()

            CartItem.objects.filter(cart__user=request.user).delete()

            transaction.on_commit(
                lambda: send_order_emails_async(order)
            )

        messages.success(
            request,
            "Payment reference received. Your payment is under verification."
        )

        return redirect("order_detail", order_id=order_id)


# ==============================
# CASH ON DELIVERY
# ==============================
@login_required
def cod_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    with transaction.atomic():
        order.payment_method = "COD"
        order.status = "PENDING"
        order.save()

        Payment.objects.get_or_create(
            order=order,
            defaults={
                "user": request.user,
                "amount": order.total_amount,
                "status": "PENDING",
            },
        )

        CartItem.objects.filter(cart__user=request.user).delete()

        transaction.on_commit(
            lambda: send_order_emails_async(order)
        )

    messages.success(
        request,
        "Your order has been placed successfully with Cash on Delivery."
    )

    return redirect("order_detail", order_id=order.id)
