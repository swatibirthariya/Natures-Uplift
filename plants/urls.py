from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/<int:pk>/', views.plant_detail, name='plant_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-sim/', views.payment_sim, name='payment_sim'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('order-success/<str:order_id>/', views.order_success, name='order_success'),
    path('reviews/', views.reviews, name='reviews'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
]
