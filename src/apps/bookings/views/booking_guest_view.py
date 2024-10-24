from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.bookings.serializers.booking_guest_serializer import (
    BookingRequestCreateSerializer,
)
from apps.bookings.services.booking_guest_service import BookingService


# 예약 요청
@extend_schema(tags=["Guest"])
class BookingRequestCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingRequestCreateSerializer
    booking_service = BookingService()

    def post(self, request, accommodation_id, room_id, *args, **kwargs):
        data = request.data.copy()
        data["accommodation_id"] = accommodation_id
        data["room_id"] = room_id

        user_data = self.booking_service.check_booker_data(data, request.user)

        serializer = self.get_serializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        self.booking_service.create_booking(serializer.validated_data, request.user)

        return Response({"message": "예약 완료"}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Guest"])
class BookingCancelView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    booking_service = BookingService()

    def patch(self, request: Request, booking_id: int, *args, **kwargs) -> Response:
        try:
            self.booking_service.cancel_booking(booking_id=booking_id)

            return Response({"message": "Booking canceled successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
