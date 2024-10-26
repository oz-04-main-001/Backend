from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.bookings.serializers.booking_guest_serializer import (
    BookingCancelSerializer,
    BookingRequestCreateSerializer,
    BookingResponseSerializer,
)
from apps.bookings.services.booking_guest_service import BookingService


@extend_schema(tags=["Guest"])
class BookingRequestCreateView(GenericAPIView):
    """예약 요청"""

    permission_classes = [IsAuthenticated]
    serializer_class = BookingRequestCreateSerializer
    booking_service = BookingService()

    @extend_schema(
        request=BookingRequestCreateSerializer,
        responses={status.HTTP_201_CREATED: BookingResponseSerializer},
    )
    def post(self, request, accommodation_id, room_id, *args, **kwargs):
        """
        숙소_id와 room_id를 path parameter로 받아서 해당 숙소의 해당 room에 대해 예약을 요청합니다.
        """
        data = request.data.copy()

        context = {"accommodation_id": accommodation_id, "room_id": room_id, "user": request.user}

        serializer = self.get_serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)

        self.booking_service.create_booking(serializer.validated_data, request.user)

        response_serializer = BookingResponseSerializer({"message": "예약 완료"})

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)




@extend_schema(tags=["Guest"])
class BookingCancelView(GenericAPIView):
    """예약 취소"""

    permission_classes = [IsAuthenticated]
    serializer_class = BookingCancelSerializer
    booking_service = BookingService()

    @extend_schema(
        request=BookingCancelSerializer,
        responses={status.HTTP_200_OK: BookingResponseSerializer},
    )
    def patch(self, request: Request, booking_id: int, *args, **kwargs) -> Response:
        """
        예약 ID를 path parameter로 받아서 해당 예약을 취소합니다.
        """

        serializer = self.get_serializer(data=request.data, context={"booking_id": booking_id})
        serializer.is_valid(raise_exception=True)

        booking = serializer.context["booking"]

        self.booking_service.cancel_booking(booking=booking)

        response_serializer = BookingResponseSerializer({"message": "Booking canceled successfully."})

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
