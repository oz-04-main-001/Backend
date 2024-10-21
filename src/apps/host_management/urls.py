from django.urls import path
from apps.host_management.views.host_booking_view import BookingListView, BookingRequestCheckView

urlpatterns = [
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('bookings/<int:pk>/action/', BookingRequestCheckView.as_view(), name='booking-action'),
]