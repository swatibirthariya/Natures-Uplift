from django.contrib import admin
from django.utils.html import format_html
from .models import Plant, Review


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'size',
        'price',
        'available',
        'category',
        'image_preview'
    )
    list_filter = ('category', 'available')
    search_fields = ('name',)
    list_editable = ('price', 'available')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" style="border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return "-"

    image_preview.short_description = "Image"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'approved', 'created_at')
    list_editable = ('approved',)
    list_filter = ('approved', 'rating')
    search_fields = ('name', 'message')
