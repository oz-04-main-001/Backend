from datetime import date

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.host_management.serializers import BookingSerializer


class BookingListView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Booking.objects.all()

    def get(self, request, *args, **kwargs):
        selected_date = self.request.query_params.get("date", None)
        accommodation_id = self.request.query_params.get("room_id", None)

        if selected_date and accommodation_id:
            selected_date = date.fromisoformat(selected_date)
            booking_list = Booking.objects.filter(
                Q(check_in_date=selected_date) | Q(check_out_date=selected_date),
                accommodation_id=accommodation_id,
            )
            serializer = BookingSerializer(booking_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "날짜를 선택 해 주세요."}, status=status.HTTP_400_BAD_REQUEST)


class BookingRequestCheckView(generics.GenericAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  # JWT 인증 필요

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()  # 특정 Booking 객체 가져오기
        action = request.data.get("action")

        if action == "accept":
            booking.status = "confirmed"
        elif action == "reject":
            booking.status = "rejected"
        elif action == "Use complete":
            booking.status = "Use complete"
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        booking.save()  # 상태 저장
        return Response({"status": booking.status}, status=status.HTTP_200_OK)
