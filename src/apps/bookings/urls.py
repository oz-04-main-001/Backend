from django.urls import path

from apps.bookings.views import booking_guest_view

app_name = "bookings"  # 앱 이름 설정

urlpatterns: list = [
    path(
        "request/<int:accommodation_id>/<int:room_id>",
        booking_guest_view.BookingRequestCreateView.as_view(),
        name="booking_request",
    ),
    path("cancel/<int:booking_id>/", booking_guest_view.BookingCancelView.as_view(), name="booking_cancel"),
]
