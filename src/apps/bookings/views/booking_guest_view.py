from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from apps.bookings.models import Booking
from apps.bookings.serializers.booking_guest_serializer import (
    BookingCancelSerializer,
    BookingReqeustCreateSerializer,
)


# 예약 요청
class BookingRequestCreateView(CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingReqeustCreateSerializer


# 예약 취소 요청
class BookingCancelView(RetrieveUpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCancelSerializer
    lookup_field = "pk"  # 예약을 id로 찾음
