from datetime import date
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from apps.bookings.models import Booking
from apps.rooms.models import Room
from apps.host_management.serializers.host_booking import BookingSerializer

# BookingListView 업데이트
class BookingListView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Booking.objects.all()

    def get(self, request, *args, **kwargs):
        selected_date = self.request.query_params.get("date", None)
        room_id = self.request.query_params.get("room_id", None)
        guest_id = self.request.query_params.get("guest_id", None)
        accommodation_id = self.request.query_params.get("accommodation_id", None)

        try:
            if guest_id:
                bookings = Booking.objects.filter(guest_id=guest_id)
            elif accommodation_id:
                bookings = Booking.objects.filter(room__accommodation_id=accommodation_id)
            else:
                bookings = Booking.objects.all()

            if selected_date and room_id:
                selected_date = date.fromisoformat(selected_date)
                rooms = Room.objects.filter(id=room_id, is_available=True)
                if not rooms.exists():
                    return Response({"detail": "해당 방은 예약이 불가능합니다."}, status=status.HTTP_400_BAD_REQUEST)
                booking_list = bookings.filter(
                    Q(check_in_date__lte=selected_date) & Q(check_out_date__gte=selected_date),
                    room_id=room_id,
                )
                serializer = BookingSerializer(booking_list, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response({"detail": "날짜를 선택 해 주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "잘못된 날짜 형식입니다."}, status=status.HTTP_400_BAD_REQUEST)

# BookingRequestCheckView 업데이트
class BookingRequestCheckView(generics.GenericAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()
        action = request.data.get("action")

        if action == "accept":
            booking.status = "confirmed"
        elif action == "reject":
            booking.status = "rejected"
        elif action == "use_complete":
            booking.status = "use_complete"
        elif action == "canceled":
            booking.status = "canceled"
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        booking.save()
        return Response({"status": booking.status}, status=status.HTTP_200_OK)