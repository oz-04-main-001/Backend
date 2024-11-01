from django.urls import path

from . import views
from .views import (
    accommodation_view,
    booking_request_view,
    booking_status_view,
    main_view,
    mypage_view,
    room_view,
)

app_name = "pages"  # 앱 이름 설정

urlpatterns = [
    path("main/", main_view.MainListView.as_view(), name="main_list"),
    path(
        "accommodations/<int:accommodation_id>/",
        accommodation_view.AccommodationDetailView.as_view(),
        name="accommodation_detail",
    ),
    path("accommodations/<int:accommodation_pk>/<int:pk>/", room_view.RoomDetailView.as_view(), name="room_detail"),
    path(
        "bookings/request/<int:accommodation_pk>/<int:pk>/",
        booking_request_view.BookingRequestView.as_view(),
        name="booking_request",
    ),
    path("bookings/status/<int:pk>/", booking_status_view.BookingStatusView.as_view(), name="booking_status"),
    path("mypage/", mypage_view.MyBookingListView.as_view(), name="my_booking_list"),
]
