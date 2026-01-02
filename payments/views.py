from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment
from accounts.models import Order, CartItem
from accounts.models import CartItem



UPI_ID = "6366382516@ybl"


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

    messages.success(
        request,
        "Your order has been placed successfully with Cash on Delivery."
    )

    return redirect("order_detail", order_id=order.id)
    CartItem.objects.filter(cart__user=request.user).delete()

