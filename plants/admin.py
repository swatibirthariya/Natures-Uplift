from django.contrib import admin
from django.utils.html import format_html
from .models import Plant, Order, OrderItem, Review

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    # Show fields in list view
    list_display = ('name', 'size', 'price', 'available', 'get_category_display', 'image_preview')
    list_filter = ('category', 'available')  # Sidebar filter for categories
    search_fields = ('name', 'category')
    list_editable = ('price', 'available')

    # Show image thumbnail in admin list
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'

    # Style the category dropdown in add/edit form
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "category":
            if 'widget' in kwargs:
                kwargs['widget'].attrs.update({'class': 'form-control'})
        return super().formfield_for_choice_field(db_field, request, **kwargs)

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
