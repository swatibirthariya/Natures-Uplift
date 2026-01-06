from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),

    path('social/<str:provider>/', views.social_login_redirect, name='social_login'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path("account/profile/", views.account_profile, name="account_profile"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("cart/increase/<int:item_id>/", views.increase_qty, name="increase_qty"),
    path("cart/decrease/<int:item_id>/", views.decrease_qty, name="decrease_qty"),
    path("", views.view_cart, name="view_cart"),
    path("add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
]
