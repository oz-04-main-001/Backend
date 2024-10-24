from django.urls import path

from apps.host_management.views.host_booking_view import (
    BookingCheckView,
    BookingRequestCheckView,
    CompleteBookingsView,
    MyAccommodationListView,
)

# MyAccommodationsUpdateView, MyAccommodationsDeleteView, MyRoomsUpdateView, MyRoomsDeleteView,

app_name = "host_management"

urlpatterns = [
    path("bookingcheck/", BookingCheckView.as_view(), name="host-management-booking-check"),
    path("requestcheck/", BookingRequestCheckView.as_view(), name="host-management-request-check"),
    path("Completebooking/", CompleteBookingsView.as_view(), name="host-management-complete-bookings"),
    # path('accommodation/update/',MyAccommodationsUpdateView.as_view(), name='host-management-my-accommodations',),
    # path('accommodation/delete/', MyAccommodationsDeleteView.as_view(), name='host-management-my-accommodations-delete',),
    # path('room/update/', MyRoomsUpdateView.as_view(), name='host-management-my-rooms',),
    # path('room/delete/', MyRoomsDeleteView.as_view(), name='host-management-my-rooms-delete',),
    path(
        "accommodation/list/",
        MyAccommodationListView.as_view(),
        name="host-management-my-accommodations-list",
    ),
]
