from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
import random
import string
from django.db.models import F

from .models import User, City, Category, Service, Cart, Booking, Payment, Review, BookingService
from .serializers import (
    UserSerializer, LoginSerializer, CitySerializer, SetLocationSerializer,
    CategorySerializer, ServiceSerializer, AddToCartSerializer, CartItemSerializer,
    ConfirmBookingSerializer, BookingResponseSerializer, InitiatePaymentSerializer,
    PaymentStatusSerializer, BookingHistorySerializer, SubmitRatingSerializer,
    AdminAddServiceSerializer, AdminUserListSerializer, AdminBookingListSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User registered successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)

class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        password = request.data.get('password')

        user = authenticate(request, username=phone, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user_id": user.id}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]

class SetUserLocationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        city_name = serializer.validated_data['city']
        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']

        try:
            user = User.objects.get(id=user_id)
            return Response({"message": f"Location set for user {user.username} to {city_name}"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ServiceByCategoryView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        try:
            category = Category.objects.get(id=category_id)
            return Service.objects.filter(category=category)
        except Category.DoesNotExist:
            return Service.objects.none()

class AddServiceToCartView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        service_id = serializer.validated_data['service_id']
        quantity = serializer.validated_data['quantity']

        try:
            user = User.objects.get(id=user_id)
            service = Service.objects.get(id=service_id)

            cart_item, created = Cart.objects.get_or_create(user=user, service=service, defaults={'quantity': quantity})
            if not created:
                cart_item.quantity += quantity
            cart_item.save()
            return Response({"message": "Service added to cart successfully"}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, Service.DoesNotExist):
            return Response({"detail": "User or Service not found"}, status=status.HTTP_404_NOT_FOUND)

class ViewCartView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                queryset = Cart.objects.filter(user=user).select_related('service').annotate(total=F('quantity') * F('service__price'))
                return queryset
            except User.DoesNotExist:
                return Cart.objects.none()
        return Cart.objects.none()

class ChooseTimeslotView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service_id = request.query_params.get('service_id')
        date_str = request.query_params.get('date')

        if not service_id or not date_str:
            return Response({"detail": "service_id and date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.get(id=service_id)
            available_timeslots = [
                "10:00 AM", "12:00 PM", "3:00 PM", "5:00 PM"
            ]
            return Response(available_timeslots, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response({"detail": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmBookingView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConfirmBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        cart_ids = serializer.validated_data['cart_ids']
        date = serializer.validated_data['date']
        timeslot = serializer.validated_data['timeslot']
        address = serializer.validated_data['address']

        try:
            user = User.objects.get(id=user_id)
            cart_items = Cart.objects.filter(id__in=cart_ids, user=user).select_related('service')

            if not cart_items.exists():
                return Response({"detail": "No valid cart items found for booking"}, status=status.HTTP_400_BAD_REQUEST)

            total_amount = sum(item.quantity * item.service.price for item in cart_items)

            with transaction.atomic():
                booking_id = 'YM' + ''.join(random.choices(string.digits, k=6))
                while Booking.objects.filter(booking_id=booking_id).exists():
                    booking_id = 'YM' + ''.join(random.choices(string.digits, k=6))

                booking = Booking.objects.create(
                    user=user,
                    booking_id=booking_id,
                    date=date,
                    timeslot=timeslot,
                    address=address,
                    total_amount=total_amount,
                    status='Confirmed'
                )

                for item in cart_items:
                    BookingService.objects.create(
                        booking=booking,
                        service=item.service,
                        quantity=item.quantity,
                        price_at_booking=item.service.price
                    )
                    item.delete()

            response_serializer = BookingResponseSerializer(booking)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred during booking: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InitiatePaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking_id = serializer.validated_data['booking_id']
        payment_method = serializer.validated_data['payment_method']

        try:
            booking = Booking.objects.get(booking_id=booking_id)
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={'payment_method': payment_method, 'status': 'Pending'}
            )
            if not created:
                payment.payment_method = payment_method
                payment.status = 'Pending'
                payment.save()
            transaction_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            payment.transaction_id = transaction_id
            payment.status = 'Success'
            payment.save()

            return Response({
                "message": "Payment initiated successfully (dummy)",
                "transaction_id": payment.transaction_id,
                "status": payment.status
            }, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Error initiating payment: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentStatusView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentStatusSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'booking_id'

    def get_object(self):
        booking_id = self.kwargs['booking_id']
        try:
            booking = Booking.objects.get(booking_id=booking_id)
            return Payment.objects.get(booking=booking)
        except (Booking.DoesNotExist, Payment.DoesNotExist):
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"detail": "Payment status not found for this booking ID"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookingHistoryView(generics.ListAPIView):
    serializer_class = BookingHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return Booking.objects.filter(user=user).order_by('-booked_at')
            except User.DoesNotExist:
                return Booking.objects.none()
        return Booking.objects.none() 

class SubmitRatingView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubmitRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking_id = serializer.validated_data['booking_id']
        rating = serializer.validated_data['rating']
        review_text = serializer.validated_data.get('review')

        try:
            booking = Booking.objects.get(booking_id=booking_id, user=request.user)
            if booking.status != 'Completed':
                return Response({"detail": "Booking must be completed to submit a rating."}, status=status.HTTP_400_BAD_REQUEST)
            review, created = Review.objects.get_or_create(
                booking=booking,
                user=request.user,
                defaults={'rating': rating, 'review_text': review_text}
            )
            if not created:
                review.rating = rating
                review.review_text = review_text
                review.save()

            return Response({"message": "Rating submitted successfully", "review_id": review.id}, status=status.HTTP_201_CREATED)

        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found or does not belong to user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AdminAddServiceView(generics.CreateAPIView):
    queryset = Service.objects.all()
    serializer_class = AdminAddServiceSerializer
    permission_classes = [IsAuthenticated] 

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAuthenticated]

class AdminBookingListView(generics.ListAPIView):
    queryset = Booking.objects.all().order_by('-booked_at')
    serializer_class = AdminBookingListSerializer
    permission_classes = [IsAuthenticated]