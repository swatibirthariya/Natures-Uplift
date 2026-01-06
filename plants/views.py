from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .forms import CheckoutForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import uuid, decimal
from .models import Plant, Review

def seed_plants():
    if Plant.objects.count() == 0:
        samples = [
            {
                'name':'Areca Palm',
                'category':'indoor',
                'size':'Medium (60-90 cm)',
                'description':'Low-maintenance indoor palm, purifies air.',
                'price':499
            },
            {
                'name':'Snake Plant',
                'category':'low_maintenance',
                'size':'Small (20-45 cm)',
                'description':'Tough, thrives in low light; great for beginners.',
                'price':299
            },
            {
                'name':'Fiddle Leaf Fig',
                'category':'indoor',
                'size':'Large (90-150 cm)',
                'description':'Statement plant with large glossy leaves.',
                'price':1299
            },
            {
                'name':'Money Plant',
                'category':'air_purifying',
                'size':'Small (30-60 cm)',
                'description':'Fast-growing climber, easy to propagate.',
                'price':199
            },
            {
                'name':'ZZ Plant',
                'category':'low_maintenance',
                'size':'Medium (50-80 cm)',
                'description':'Very low water needs, great for offices.',
                'price':599
            },
            {
                'name':'Rubber Plant',
                'category':'indoor',
                'size':'Medium-Large (70-120 cm)',
                'description':'Bold foliage, tolerates indoor conditions.',
                'price':799
            },
        ]

        for s in samples:
            Plant.objects.create(**s)


def home(request):
    if settings.DEBUG:
        seed_plants()
    return render(request,'plants/home.html')


def plant_list(request):
    category = request.GET.get('category')

    plants = Plant.objects.all()

    if category:
        plants = plants.filter(category=category)

    return render(
        request,
        'plants/plant_list.html',
        {
            'plants': plants,
            'selected_category': category
        }
    )
def plant_detail(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    return render(request,'plants/plant_detail.html',{'plant':plant})

def is_bangalore_pincode(pin):
    if not pin: return False
    s = str(pin).strip()
    return len(s)==6 and s.startswith('56')

'''def checkout(request):
    cart = get_cart(request)
    if not cart:
        return redirect('plant_list')
    items = []
    total = decimal.Decimal('0.00')
    for pid, qty in cart.items():
        p = get_object_or_404(Plant, pk=int(pid))
        items.append({'plant':p,'qty':qty,'subtotal': p.price * qty})
        total += p.price * qty
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if not is_bangalore_pincode(cd['pincode']):
                return render(request,'plants/checkout.html',{'items':items,'total':total,'form':form,'delivery_error':'We are not delivering to this pincode.'})
            delivery_charge = decimal.Decimal('0.00')

            if cd['delivery_type'] == 'fast':
                delivery_charge = decimal.Decimal('50.00')

            total += delivery_charge
            order = Order.objects.create(order_id=str(uuid.uuid4()).replace('-','')[:12],
                                         name=cd['name'], email=cd['email'], phone=cd['phone'],
                                         pincode=cd['pincode'], delivery_type=cd['delivery_type'],
                                         total_amount=total, paid=False)
            for it in items:
                OrderItem.objects.create(order=order, plant=it['plant'], qty=it['qty'], price=it['plant'].price)
            request.session['pending_order'] = order.order_id
            return redirect('payment_sim')
    else:
        form = CheckoutForm()
    return render(request,'plants/checkout.html',{'items': items,'total': total,'form': form,'delivery_charge': delivery_charge})

def payment_sim(request):
    return render(request,'plants/payment_sim.html',{'upi':'6366382516@ybl'})

@csrf_exempt
def payment_callback(request):
    status = request.GET.get('status')
    order_id = request.session.get('pending_order')
    if not order_id:
        return redirect('home')
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return redirect('home')
    if status == 'success':
        order.paid = True
        order.save()
        request.session['cart'] = {}
        del request.session['pending_order']
        return redirect('order_success', order_id=order.order_id)
    else:
        return render(request,'plants/payment_failed.html',{})'''

def order_success(request, order_id):
    return render(request,'plants/order_success.html',{'order_id':order_id})

from django.contrib import messages

def reviews(request):
    if request.method == 'POST':
        Review.objects.create(
            name=request.POST.get('name'),
            rating=int(request.POST.get('rating', 5)),
            message=request.POST.get('message'),
            approved=False
        )
        messages.success(
            request,
            "Thank you! Your review was submitted and will appear after approval."
        )
        return redirect('reviews')

    revs = Review.objects.filter(approved=True).order_by('-created_at')
    return render(request,'plants/reviews.html',{'reviews':revs})


def contact(request):
    return render(request,'plants/contact.html')

def about(request):
    return render(request,'plants/about.html')
