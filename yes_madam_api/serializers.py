from rest_framework import serializers
from .models import User, City, Category, Service, Cart, Booking, Payment, Review, BookingService
from django.db.models import F

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class SetLocationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    city = serializers.CharField(max_length=100)
    latitude = serializers.CharField(max_length=50)
    longitude = serializers.CharField(max_length=50)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'duration', 'description']

class AddToCartSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'service', 'quantity', 'total', 'added_at']

class BookingServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = BookingService
        fields = ['service_name', 'quantity', 'price_at_booking']

class BookingResponseSerializer(serializers.ModelSerializer):
    services = BookingServiceSerializer(source='bookingservice_set', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'date', 'timeslot', 'address', 'total_amount', 'status', 'booked_at', 'services']

class ConfirmBookingSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    cart_ids = serializers.ListField(child=serializers.IntegerField())
    date = serializers.DateField()
    timeslot = serializers.CharField(max_length=50)
    address = serializers.CharField()

class InitiatePaymentSerializer(serializers.Serializer):
    booking_id = serializers.CharField(max_length=20)
    payment_method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)

class PaymentStatusSerializer(serializers.ModelSerializer):
    booking_id = serializers.CharField(source='booking.booking_id', read_only=True)

    class Meta:
        model = Payment
        fields = ['booking_id', 'payment_method', 'transaction_id', 'status', 'paid_at']

class BookingHistorySerializer(serializers.ModelSerializer):
    services = BookingServiceSerializer(source='bookingservice_set', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id', 'date', 'timeslot', 'status', 'total_amount', 'services']

class SubmitRatingSerializer(serializers.Serializer):
    booking_id = serializers.CharField(max_length=20)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review = serializers.CharField(required=False, allow_blank=True)

class AdminAddServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'price', 'duration', 'description']

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'is_active', 'date_joined']

class AdminBookingListSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    services = BookingServiceSerializer(source='bookingservice_set', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'booking_id', 'user_username', 'date', 'timeslot', 'address', 'total_amount', 'status', 'booked_at', 'services']