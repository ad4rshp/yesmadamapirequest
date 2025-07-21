from django.urls import path
from .views import (
    RegisterView, LoginView, CityListView, SetUserLocationView,
    CategoryListView, ServiceByCategoryView, AddServiceToCartView, ViewCartView,
    ChooseTimeslotView, ConfirmBookingView, InitiatePaymentView, PaymentStatusView,
    BookingHistoryView, SubmitRatingView, AdminAddServiceView, AdminUserListView,
    AdminBookingListView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('cities/', CityListView.as_view(), name='city-list'),
    path('set-location/', SetUserLocationView.as_view(), name='set-location'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/services/', ServiceByCategoryView.as_view(), name='services-by-category'),
    path('cart/add/', AddServiceToCartView.as_view(), name='add-to-cart'),
    path('cart/', ViewCartView.as_view(), name='view-cart'),
    path('timeslots/', ChooseTimeslotView.as_view(), name='choose-timeslot'),
    path('book/', ConfirmBookingView.as_view(), name='confirm-booking'),
    path('payment/initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payment/status/<str:booking_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('bookings/', BookingHistoryView.as_view(), name='booking-history'),
    path('rate/', SubmitRatingView.as_view(), name='submit-rating'),
    path('admin/services/add/', AdminAddServiceView.as_view(), name='admin-add-service'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/bookings/', AdminBookingListView.as_view(), name='admin-booking-list'),
]