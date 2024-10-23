from django.urls import path
from apps.host_management.views.host_booking_view import BookingCheckView, BookingRequestCheckView, CompleteBookingsView

app_name = "host_management"

urlpatterns = [
    path('bookingcheck/', BookingCheckView.as_view(), name='host-management-booking-check'),
    path('requestcheck/', BookingRequestCheckView.as_view(), name='host-management-request-check'),
    path('Completebooking/', CompleteBookingsView.as_view(), name='host-management-complete-bookings'),
]
