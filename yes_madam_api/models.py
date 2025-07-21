from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return self.username

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'service')

    def __str__(self):
        return f"Cart for {self.user.username}: {self.quantity} x {self.service.name}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    booking_id = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    timeslot = models.CharField(max_length=50)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    booked_at = models.DateTimeField(auto_now_add=True)
    services = models.ManyToManyField(Service, through='BookingService')

    def __str__(self):
        return f"Booking {self.booking_id} by {self.user.username}"

class BookingService(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('booking', 'service')

    def __str__(self):
        return f"{self.quantity} x {self.service.name} for Booking {self.booking.booking_id}"

class Payment(models.Model):
    METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Cash', 'Cash'),
    ]
    STATUS_CHOICES = [
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Pending', 'Pending'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking.booking_id}: {self.status}"

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking.booking_id} by {self.user.username} - Rating: {self.rating}"