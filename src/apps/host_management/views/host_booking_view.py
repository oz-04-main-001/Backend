from datetime import date

from drf_spectacular.utils import extend_schema
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accommodations.models import Accommodation
from apps.bookings.models import Booking
from apps.host_management.serializers.host_booking import BookingSerializer


@extend_schema(tags=["Host"])
class BookingCheckView(generics.GenericAPIView):
    """예약 내역 관리"""

    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        호스트가 예약 내역을 관리하는 기능
        날짜의 값을 쿼리파라미터로 받아와야 함
        """

        host = request.user

        selected_date = self.request.query_params.get("date", None)

        try:
            if selected_date:
                # 호스트가 등록한 숙소 가져오기
                accommodations = Accommodation.objects.filter(host=host)
                accommodation_ids = accommodations.values_list('id', flat=True)

                # 선택한 날짜에 예약이 있는 숙소 목록 필터링
                selected_date = date.fromisoformat(selected_date)
                booking_list = Booking.objects.filter(
                    check_in_date__lte=selected_date, check_out_date__gte=selected_date,
                    room__accommodation_id__in=accommodation_ids,
                )
                serializer = BookingSerializer(booking_list, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response({"detail": "날짜를 선택 해 주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "잘못된 날짜 형식입니다."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class BookingRequestCheckView(generics.GenericAPIView):
    """예약 요청 관리"""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        게스트가 보낸 예약 요청을 수락/거절하는 기능
        클라이언트로가 patch요청을 보내면 요청 데이터로 부터 전송된 action이라는 키를 가져와야 함
        action의 값에 따라 booking.status의 값으로 반환함
        """

        booking = self.get_object()
        action = request.data.get("action")

        if action == "accept":
            booking.status = "confirmed"
        elif action == "cancelled":
            booking.status = "cancelled_by_host"
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        booking.save()
        return Response({"status": booking.status}, status=status.HTTP_200_OK)


@extend_schema(tags=["Host"])
class CompleteBookingsView(generics.ListAPIView):
    """이용 완료 내역"""
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def filter_queryset(self, queryset):
        """
        게스트가 날짜 기준으로 숙소 사용을 완료한 내역을 가져온다.
        """

        user = self.request.user
        selected_date = self.request.query_params.get("date", default=date.today())
        return queryset.filter(
            accommodation__host=user.host,
            check_in_date__lte=selected_date,
            status='completed',
        )
