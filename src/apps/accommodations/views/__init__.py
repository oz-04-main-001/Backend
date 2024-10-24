from datetime import date

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.host_management.serializers import BookingSerializer


class BookingByDateView(generics.ListAPIView):
    # 날짜별 예약 조회를 위한 뷰
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 요청에서 날짜를 가져와 필터링
        clicked_date = self.request.query_params.get("date", None)
        if clicked_date:
            clicked_date = date.fromisoformat(clicked_date)
            return Booking.objects.filter(check_in__lte=clicked_date, check_out__gte=clicked_date)
        return Booking.objects.none()


class AcceptRejectBookingView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  # JWT 인증

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()  # 특정 Booking 객체 가져오기
        action = request.data.get["action"]

        if action == "accept":
            booking.status = "confirmed"
        elif action == "reject":
            booking.status = "rejected"
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        booking.save()
        return Response({"status": booking.status}, status=status.HTTP_200_OK)
