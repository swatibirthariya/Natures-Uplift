from django.contrib import admin
from .models import Payment
from django.utils.html import format_html
from django.template.loader import render_to_string

# 🔥 IMPORT YOUR BREVO HELPER
from accounts.utils import send_brevo_email


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    # ✅ KEEP + ADD (do not remove anything you already have)
    list_display = (
        "order",
        "user",
        "amount",
        "utr_number",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("order__id", "utr_number", "user__email")

    actions = ["verify_payment_and_notify"]

    # ==============================
    # ✅ ADMIN ACTION
    # ==============================
    def verify_payment_and_notify(self, request, queryset):
        for payment in queryset:

            # Skip already verified payments
            if payment.status == "SUCCESS":
                continue

            # ✅ Update payment
            payment.status = "SUCCESS"
            payment.save()

            # ✅ Update order
            order = payment.order
            order.status = "PAID"
            order.payment_method = "UPI"
            order.save()

            # ==============================
            # ✅ CUSTOMER EMAIL (BREVO)
            # ==============================
            html_content = render_to_string(
                "emails/payment_success_email.html",
                {
                    "order": order,
                    "payment": payment,
                    "user": order.user,
                }
                )

            send_brevo_email(
                subject="Payment Verified – Natures Uplift 🌱",
                html_content=html_content,
                to_email=order.user.email,
                to_name=order.user.first_name or "Customer",
            )

    verify_payment_and_notify.short_description = (
        "✅ Verify payment & send confirmation email"
    )
