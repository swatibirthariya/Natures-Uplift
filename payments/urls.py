from django.urls import path
from . import views

urlpatterns = [
    path('start/<int:order_id>/', views.start_payment, name='start_payment'),
    path('submit-utr/<int:order_id>/', views.submit_utr, name='submit_utr'),
    path("cod/<int:order_id>/", views.cod_order, name="cod_order"),  # ✅ ADD THIS
]
