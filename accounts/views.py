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
from django.views.decorators.http import require_POST
from .models import Order, CartItem, Address
from django.utils.safestring import mark_safe

from .models import Cart, CartItem
from .forms import CheckoutForm
from accounts.models import Order
from payments.models import Payment
from .models import OrderItem
# ===== FORGOT PASSWORD =====
from django.contrib import messages
from .forms import OTPForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils.safestring import mark_safe
from plants.models import Plant


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





def forgot_password(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")

        user = (
            CustomUser.objects.filter(email=identifier).first()
            or CustomUser.objects.filter(phone=identifier).first()
        )

        if not user:
            messages.error(request, "No account found")
            return redirect("forgot_password")

        otp = str(random.randint(100000, 999999))

        request.session["reset_user_id"] = user.id
        request.session["reset_otp"] = otp
        request.session["otp_time"] = time.time()
        send_otp_email(user.email, otp)

        messages.success(request, "OTP sent to your registered email")
        return redirect("verify_otp")

    return render(request, "registration/forgot_password.html")



def verify_otp(request):
    if request.method == "POST":
        if time.time() - request.session.get("otp_time", 0) > 300:
            messages.error(request, "OTP expired")
            return redirect("forgot_password")

        if request.POST.get("otp") == request.session.get("reset_otp"):
            return redirect("reset_password")

        messages.error(request, "Invalid OTP")

    return render(request, "registration/verify_otp.html")

# ===== RESET PASSWORD =====
def reset_password(request):
    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot_password")

    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["password"])
            user.save()

            request.session.flush()
            messages.success(request, "Password reset successful")
            return redirect("login")
    else:
        form = ResetPasswordForm()

    return render(request, "registration/reset_password.html", {"form": form})

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

    delivery_charge = 85 if delivery_type == "fast" else 60
    grand_total = subtotal + delivery_charge

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            # ✅ Create order FIRST
            order = Order.objects.create(
                user=request.user,
                total_amount=grand_total,
                status="PENDING"
            )

            # ✅ Create ALL order items
            for item in cart_items:
                plant = item.product

                image_url = ""
                if plant.image:
                    image_url = plant.image.url  # Cloudinary-safe

                OrderItem.objects.create(
                    order=order,
                    plant=plant,
                    quantity=item.quantity,
                    price=plant.price,
                    plant_image_url=image_url
                )

            # ✅ Redirect AFTER loop
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

@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Plant, pk=pk)

    # ✅ CASE 1: Logged-in user → DB cart
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        item.quantity = item.quantity + 1 if not created else 1
        item.save()

    # ✅ CASE 2: Guest user → Session cart
    else:
        cart = request.session.get("cart", {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session["cart"] = cart
        request.session.modified = True

    messages.success(
        request,
        mark_safe('Item added to cart.')
    )
    # ✅ THIS IS THE FIX
    return redirect("/cart/")

def view_cart(request):

    # ---------- GUEST USER ----------
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        items = []
        total = 0

        for pk, qty in cart.items():
            plant = get_object_or_404(Plant, pk=pk)
            subtotal = plant.price * qty
            total += subtotal

            items.append({
                'product': plant,
                'quantity': qty,
                'subtotal': subtotal
            })

        return render(request, "cart/cart.html", {
            "items": items,
            "total": total,
            "guest": True
        })

    # ---------- LOGGED-IN USER ----------
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product")
    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "cart/cart.html", {
        "items": items,
        "total": total,
        "guest": False
    })
