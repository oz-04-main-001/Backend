from django.urls import path

from apps.host_management.views.host_booking_view import (
    BookingListView,
    BookingRequestCheckView,
)

app_name = "host_management"  # 앱 이름 설정

urlpatterns: list = [
    # 예: path('dashboard/', views.dashboard, name='dashboard'),
    path("bookingcheck/", BookingListView.as_view(), name="booking-Check"),
    path("requestcheck/<int:pk>/action/", BookingRequestCheckView.as_view(), name="booking-request-check"),
]
