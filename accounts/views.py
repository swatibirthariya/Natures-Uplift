from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    RegisterForm, LoginForm, OTPForm,
    ResetPasswordForm, CheckoutForm
)
from .models import CustomUser, Order
from .models import Cart
from .utils import merge_cart_after_login, send_otp_email, get_whatsapp_otp_link
import random
import time
from plants.models import Plant
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, CartItem, Address

from .models import Cart, CartItem
from .forms import CheckoutForm
from accounts.models import Order
from payments.models import Payment



@login_required
def account_profile(request):
    user = request.user

    # session based cart
    cart_id = request.session.get("cart_id")

    if cart_id:
        cart_items = CartItem.objects.filter(cart_id=cart_id)
    else:
        cart_items = []

    orders = Order.objects.filter(user=user).order_by("-created_at")
    address = Address.objects.filter(user=user).first()

    return render(request, "account/profile.html", {
        "cart_items": cart_items,
        "orders": orders,
        "address": address,
    })




# ===== LOGIN =====
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = (
                CustomUser.objects.filter(phone=identifier).first()
                or CustomUser.objects.filter(email=identifier).first()
            )

            if user:
                user_auth = authenticate(request, username=user.username, password=password)
                if user_auth:
                    login(request, user_auth)

                    # ✅ Cart sync after login
                    merge_cart_after_login(request, user_auth)
                    name = user.first_name or user.username
                    messages.success(request, f"Welcome back, {name}!")
                    return redirect('home')
                else:
                    print("Authentication failed for:", identifier)
            else:
                print("User not found:", identifier)

            messages.error(request, "Invalid credentials")
        else:
            print("Login form errors:", form.errors)
            messages.error(request, "Please fix the errors below.")
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


# ===== REGISTER =====
from django.contrib.auth import authenticate, login
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # ✅ ALWAYS set username
            user.username = user.phone or user.email
            user.set_password(form.cleaned_data['password1'])
            user.save()

            print("User created:", user.id, user.username)

            # ✅ AUTHENTICATE USER FIRST
            user = authenticate(
                request,
                username=user.username,
                password=form.cleaned_data['password1']
            )

            if user is not None:
                login(request, user)

            messages.success(
                request,
                f"Welcome {user.username}! Your account has been created."
            )
            return redirect('home')
        else:
            print("Register form errors:", form.errors)
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})



# ===== FORGOT PASSWORD =====
def forgot_password(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        try:
            user = CustomUser.objects.get(phone=phone)
            
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            request.session['phone'] = phone
            request.session['otp_time'] = time.time()

            print("Generated OTP:", otp)

            # ✅ EMAIL OTP
            if user.email:
                try:
                    send_otp_email(user.email, otp)
                    print("OTP email sent to:", user.email)
                    messages.success(request, f"OTP sent to your email: {user.email}")
                except Exception as e:
                    print("Email sending error:", e)
                    messages.error(request, "Failed to send OTP email.")

            # ✅ WHATSAPP OTP LINK
            whatsapp_link = get_whatsapp_otp_link(phone, otp)

            return render(request, 'registration/verify_otp.html', {
                'form': OTPForm(),
                'whatsapp_link': whatsapp_link
            })

        except CustomUser.DoesNotExist:
            print("Phone not registered:", phone)
            messages.error(request, "Phone number not registered")

    return render(request, 'registration/forgot_password.html')


# ===== VERIFY OTP =====
def verify_otp(request):
    if request.method == 'POST':
        otp_time = request.session.get('otp_time', 0)

        if time.time() - otp_time > 300:
            messages.error(request, "OTP expired")
            return redirect('forgot_password')

        if request.POST.get('otp') == request.session.get('otp'):
            messages.success(request, "OTP verified successfully!")
            return redirect('reset_password')

        messages.error(request, "Invalid OTP")

    return render(request, 'registration/verify_otp.html', {'form': OTPForm()})


# ===== RESET PASSWORD =====
def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.get(phone=request.session.get('phone'))
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Password reset successful")
            return redirect('login')
        else:
            print("Reset password form errors:", form.errors)
            messages.error(request, "Please fix the errors below.")
    else:
        form = ResetPasswordForm()
    return render(request, 'registration/reset_password.html', {'form': form})


# ===== CHECKOUT =====
@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("view_cart")

    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("view_cart")

    subtotal = sum(item.get_total_price() for item in cart_items)
    delivery_type = request.POST.get("delivery_type", "fast")

    if delivery_type == "fast":
        delivery_charge = 85
    else:
        delivery_charge = 60
    grand_total = subtotal + delivery_charge

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            order = Order.objects.create(
                user=request.user,
                total_amount=grand_total,
                status="PENDING"
            )

            # 🔥 DO NOT DELETE CART HERE
            return redirect("start_payment", order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, "cart/checkout.html", {
        "form": form,
        "items": cart_items,
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total,
    })




# ===== SOCIAL LOGIN PLACEHOLDER =====
def social_login_redirect(request, provider):
    return redirect('home')




def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = Payment.objects.filter(order=order).first()

    return render(request, "orders/order_detail.html", {
        "order": order,
        "payment": payment
    })

def cart_view(request):
    cart = None
    items = []
    total = 0

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related("product")

        total = sum(item.get_total_price() for item in items)

    context = {
        "cart": cart,
        "items": items,
        "total": total
    }
    return render(request, "cart/cart.html", context)

def increase_qty(request, item_id):
    item = CartItem.objects.get(id=item_id, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect("view_cart")


def decrease_qty(request, item_id):
    item = CartItem.objects.get(id=item_id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect("view_cart")

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Plant, pk=pk)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1
    else:
        item.quantity = 1

    item.save()

    return redirect("view_cart")

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product")

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "cart/cart.html", {
        "items": items,
        "total": total
    })