from django.urls import path
from apps.host_management.views.host_booking_view import BookingListView, BookingRequestCheckView

urlpatterns = [
    path('host-management/', BookingListView.as_view(), name='host-management-booking-list'),
    path('host-management/<int:pk>/action/', BookingRequestCheckView.as_view(), name='host-management-booking-action'),
]
