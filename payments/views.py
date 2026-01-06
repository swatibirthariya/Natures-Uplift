from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment
from accounts.models import Order, CartItem
from accounts.models import CartItem
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.db import transaction


UPI_ID = "6366382516@ybl"


def send_order_emails(order):
    user = order.user
    items = order.items.all()
    # 📧 CUSTOMER EMAIL (only if exists)
    if user.email:
        send_mail(
            subject="Your order with Natures Uplift 🌱",
            message=f"""
        Hi {user.first_name or user.username},

        Thank you for shopping with Natures Uplift 🌿

        Order ID: {order.id}
        Total Amount: ₹{order.total_amount}
        Payment Method: {order.payment_method}

        Your order is currently being processed.
        We will notify you once it is shipped.

        Regards,
        Natures Uplift
        """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

    html_content = render_to_string(
        "emails/admin_order_email.html",
        {
            "order": order,
            "items": items,   # ✅ now defined
        }
    )

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject="New Order Received – Natures Uplift 🌱",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.ADMIN_EMAIL,
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


@login_required
def start_payment(request, order_id):
    print("START PAYMENT HIT", order_id)
    order = get_object_or_404(Order, id=order_id, user=request.user)

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'user': request.user,
            'amount': order.total_amount
        }
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

    return render(request, "payments/upi_payment.html", {
        "order": order,
        "payment": payment,
        "gpay_link": gpay_link,
        "phonepe_link": phonepe_link,
    })



@login_required
def submit_utr(request, order_id):
    payment = get_object_or_404(Payment, order_id=order_id, user=request.user)
    order = payment.order  # ✅ FIX

    if request.method == "POST":
        utr = request.POST.get("utr")

        if not utr:
            messages.error(request, "Please enter payment reference")
            return redirect("start_payment", order_id=order_id)

        payment.utr_number = utr
        payment.status = "UNDER_REVIEW"   # ✅ FIX
        payment.save()

        order.payment_method = "UPI"      # ✅ FIX
        order.status = "PENDING"
        order.save()

        # ✅ CLEAR CART
        CartItem.objects.filter(cart__user=request.user).delete()
        transaction.on_commit(
            lambda: send_order_emails(order)
        )
        messages.success(
            request,
            "Payment reference received. Your payment is under verification."
        )

        return redirect("order_detail", order_id=order_id)

    
@login_required
def cod_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    order.payment_method = "COD"
    order.status = "PENDING"
    order.save()

    Payment.objects.get_or_create(
        order=order,
        defaults={
            "user": request.user,
            "amount": order.total_amount,
            "status": "PENDING"
        }
    )

    # ✅ CLEAR CART
    CartItem.objects.filter(cart__user=request.user).delete()
    transaction.on_commit(
            lambda: send_order_emails(order)
        )
    messages.success(
        request,
        "Your order has been placed successfully with Cash on Delivery."
    )

    return redirect("order_detail", order_id=order.id)
    CartItem.objects.filter(cart__user=request.user).delete()

