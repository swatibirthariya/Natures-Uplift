from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, CustomUser, Address


admin.site.register(CustomUser)
admin.site.register(Address)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'plant',
        'quantity',
        'price',
        'plant_image_preview'
    )

    def plant_image_preview(self, obj):
        if obj.plant_image_url:
            return format_html(
                '<img src="{}" width="60" style="border-radius:6px;" />',
                obj.plant_image_url
            )
        return "-"

    plant_image_preview.short_description = "Plant Image"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'total_amount',
        'status',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

