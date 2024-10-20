from django.urls import path

from . import views
from .views import (
    booking_request_view,
    booking_status_view,
    hotel_view,
    main_view,
    room_view,
)

app_name = "pages"  # 앱 이름 설정

urlpatterns = [
    path("main/", main_view.MainListView.as_view(), name="main_list"),
    path("accommodations/<int:pk>/", hotel_view.HotelDetailView.as_view(), name="hotel_detail"),
    path("accomodations/<int:hotel_pk>/<int:pk>/", room_view.RoomDetailView.as_view(), name="room_detail"),
    path(
        "bookings/request/<int:hotel_pk>/<int:pk>/",
        booking_request_view.BookingRequestView.as_view(),
        name="booking_request",
    ),
    path("bookings/status/<int:pk>/", booking_status_view.BookingStatusView.as_view(), name="booking_status"),
]
