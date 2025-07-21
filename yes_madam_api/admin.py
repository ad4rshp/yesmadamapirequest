from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, City, Category, Service, Cart, Booking, Payment, Review, BookingService

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone',)}),
    )

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'duration')
    list_filter = ('category',)
    search_fields = ('name', 'description')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'quantity', 'added_at')
    list_filter = ('user', 'service')
    search_fields = ('user__username', 'service__name')
    raw_id_fields = ('user', 'service')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_id', 'user', 'date', 'timeslot', 'total_amount', 'status')
    list_filter = ('status', 'date')
    search_fields = ('booking_id', 'user__username', 'address')
    raw_id_fields = ('user',)

@admin.register(BookingService)
class BookingServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'service', 'quantity', 'price_at_booking')
    raw_id_fields = ('booking', 'service')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'payment_method', 'status', 'transaction_id', 'paid_at')
    list_filter = ('payment_method', 'status')
    search_fields = ('booking__booking_id', 'transaction_id')
    raw_id_fields = ('booking',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('booking__booking_id', 'user__username', 'review_text')
    raw_id_fields = ('booking', 'user')