from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Payment
from accounts.models import Order
from payments.views import send_brevo_email


@receiver(post_save, sender=Payment)
def payment_success_handler(sender, instance, created, **kwargs):
    """
    Trigger customer email when payment becomes SUCCESS
    """

    if instance.status == "SUCCESS":
        order = instance.order
        user = instance.user

        # Avoid duplicate emails
        if order.status != "PAID":
            order.status = "PAID"
            order.save(update_fields=["status"])

            if user.email:
                html_content = render_to_string(
                    "emails/payment_success_email.html",
                    {
                        "order": order,
                        "payment": instance,
                        "user": user,
                    }
                )

                send_brevo_email(
                    subject="Payment Confirmed – Natures Uplift 🌱",
                    html_content=html_content,
                    to_email=user.email,
                )
