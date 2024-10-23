from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.bookings.serializers.booking_guest_serializer import (
    BookingCancelSerializer,
    BookingReqeustCreateSerializer,
)
from apps.bookings.services.booking_guest_service import BookingService


# 예약 요청
@extend_schema(tags=["Guest"])
class BookingRequestCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingReqeustCreateSerializer
    booking_service = BookingService()

    def post(self, request, accommodation_id, room_id, *args, **kwargs):
        data = request.data.copy()
        data["accommodation_id"] = accommodation_id
        data["room_id"] = room_id

        user_data = BookingService.check_booker_data(data, request.user)

        serializer = self.get_serializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        BookingService.create_booking(serializer.validated_data, request.user)

        return Response({"message": "예약 완료"}, status=status.HTTP_201_CREATED)


# 예약 취소 요청
@extend_schema(tags=["Guest"])
class BookingCancelView(RetrieveUpdateAPIView):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCancelSerializer
    lookup_field = "pk"  # 예약을 id로 찾음
