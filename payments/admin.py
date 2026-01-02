from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'amount', 'utr_number', 'status')
    list_filter = ('status',)
    search_fields = ('utr_number',)
