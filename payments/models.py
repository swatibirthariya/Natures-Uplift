from django.db import models
from django.conf import settings
from accounts.models import Order

class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('UNDER_REVIEW', 'Under Review'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    upi_id = models.CharField(max_length=100, default='6366382516@ybl')
    utr_number = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.id} - {self.status}"
