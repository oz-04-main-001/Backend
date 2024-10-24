from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accommodations.models import Accommodation
from apps.bookings.models import Booking
from apps.common.permissions.host_permission import IsHost
from apps.host_management.serializers.host_management_serializers import (
    BookingSerializer,
    BookingCheckSerializer,
    BookingRequestCheckSerializer,
    BookingStatisticsSerializer,
    AccommodationHostManagementSerializer,
)


@extend_schema(tags=["Host-Management"])
class BookingCheckView(generics.GenericAPIView):
    """예약 내역 관리"""

    serializer_class = BookingCheckSerializer
    permission_classes = (IsAuthenticated, IsHost)

    @extend_schema(
        request=BookingRequestCheckSerializer,
        responses={status.HTTP_200_OK: BookingSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="date",
                description="Check bookings for this date (YYYY-MM-DD)",
                required=True,
                type=OpenApiTypes.DATE,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        """
        호스트가 예약 내역을 관리하는 기능
        날짜의 값을 쿼리파라미터로 받아와야 함
        """
        # 호스트 유저 가져오기
        host = request.user.business_profile

        # serializer로 날짜 검증하기
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        selected_date = serializer.validated_data.get("date")

        # 호스트가 등록한 숙소 가져오기
        accommodations = Accommodation.objects.filter(host=host)

        accommodation_ids = accommodations.values_list("id", flat=True)

        # 선택한 날짜에 예약이 있는 숙소 목록 필터링
        booking_list = Booking.objects.filter(
            check_in_datetime__lte=selected_date,
            check_out_datetime__gte=selected_date,
            room__accommodation_id__in=accommodation_ids,
        )

        # 예약 리스트를 직렬화 후 응답
        serializer = BookingSerializer(booking_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Host-Management"])
class BookingRequestCheckView(generics.GenericAPIView):
    """예약 요청 관리"""

    serializer_class = BookingRequestCheckSerializer
    permission_classes = (IsAuthenticated, IsHost)

    @extend_schema(
        request=BookingRequestCheckSerializer,
        responses={status.HTTP_200_OK: BookingSerializer},
    )
    def patch(self, request):
        """
        게스트가 보낸 예약 요청을 수락/거절하는 기능
        클라이언트로가 patch요청을 보내면 요청 데이터로 부터 전송된 action이라는 키를 가져와야 함
        action의 값에 따라 booking.status의 값으로 반환함
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.context["booking"]
        action = serializer.validated_data["action"]

        if action == "accept":
            booking.status = "confirmed"
        if action == "cancelled":
            booking.status = "cancelled_by_host"

        booking.save()
        return Response(
            {"message": "예약 요청이 성공했습니다", "status": booking.status},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Host-Management"])
class CompleteBookingsView(generics.GenericAPIView):
    """이용 완료 내역"""

    permission_classes = (IsAuthenticated, IsHost)
    serializer_class = BookingStatisticsSerializer

    @extend_schema(
        request=BookingStatisticsSerializer,
        responses={status.HTTP_200_OK: BookingSerializer},
        parameters=[
            OpenApiParameter(
                name="date",
                description="Check bookings for this date (YYYY-MM-DD)",
                required=False,
                type=OpenApiTypes.DATE,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        """
        GET 요청을 처리하여 완료된 예약 내역을 반환합니다.
        date parameter가 없을 시 현재 시간을 기준으로 완료된 예약 내역을 반환합니다.
        """
        user = request.user.business_profile

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        selected_date = serializer.validated_data.get("date") or date.today()

        booking_list = Booking.objects.filter(
            room__accommodation__host=user,
            check_out_datetime__lte=selected_date,
            status="completed",
        )

        serializer = BookingSerializer(booking_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Host-Management"])
class MyAccommodationListView(generics.GenericAPIView):
    """숙소 내역 조회"""

    permission_classes = (IsAuthenticated, IsHost)
    serializer_class = AccommodationHostManagementSerializer

    @extend_schema(
        responses={status.HTTP_200_OK: AccommodationHostManagementSerializer(many=True)},
        description="호스트가 등록한 모든 활성 숙소 목록을 반환합니다.",
    )
    def get(self, request, *args, **kwargs):
        """GET 요청을 처리하여 숙소 목록을 반환합니다."""
        queryset = Accommodation.objects.filter(host=request.user.business_profile, is_active=True)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
