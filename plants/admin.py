from django.contrib import admin
from .models import Plant, Order, OrderItem, Review

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name','size','price','available')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('plant','qty','price')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id','name','pincode','total_amount','paid','created_at')
    inlines = [OrderItemInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name','rating','approved','created_at')
    list_editable = ('approved',)
