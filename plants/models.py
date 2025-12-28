from django.db import models
from cloudinary.models import CloudinaryField

class Plant(models.Model):

    CATEGORY_CHOICES = [
        ('indoor', 'Indoor Plants'),
        ('outdoor', 'Outdoor Plants'),
        ('low_maintenance', 'Low Maintenance Plants'),
        ('air_purifying', 'Air Purifying Plants'),
        ('pet_friendly', 'Pet Friendly Plants'),
        ('flowering', 'Flowering Plants'),
        ('fruit', 'Fruit Plants'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )
    size = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = CloudinaryField('image', blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    pincode = models.CharField(max_length=10)
    delivery_type = models.CharField(max_length=20, choices=(('normal','Normal'),('fast','Fast')))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.order_id

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Review(models.Model):
    name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(default=5)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
