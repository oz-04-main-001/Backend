from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accommodations.models import Accommodation
from apps.bookings.models import Booking
from apps.host_management.serializers.host_management_serializers import (
    AccommodationSerializer,
    BookingSerializer,
    BookingCheckSerializer,
    BookingRequestCheckSerializer,
)


@extend_schema(tags=["Host-Management"])
class BookingCheckView(generics.GenericAPIView):
    """예약 내역 관리"""

    serializer_class = BookingCheckSerializer
    permission_classes = (IsAuthenticated,)

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
    permission_classes = [IsAuthenticated]

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
class CompleteBookingsView(generics.ListAPIView):
    """이용 완료 내역"""

    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def filter_queryset(self, queryset):
        """
        게스트가 날짜 기준으로 숙소 사용을 완료한 내역을 가져온다.
        """
        user = self.request.user.business_profile
        selected_date = self.request.query_params.get("date", default=date.today())
        return queryset.filter(
            accommodation__host=user.host,
            check_in_date__lte=selected_date,
            status="completed",
        )


@extend_schema(tags=["Host-Management"])
class MyAccommodationListView(generics.ListAPIView):
    """숙소 내역 조회"""

    permission_classes = [IsAuthenticated]
    serializer_class = AccommodationSerializer

    def get_queryset(self):
        """
        호스트가 등록한 모든 숙소를 반환합니다.
        """
        return Accommodation.objects.filter(host=self.request.user.business_profile, is_active=True)


# @extend_schema(tags=["Host-Management"])
# class MyAccommodationsUpdateView(generics.GenericAPIView):
#     """숙소 편집"""
#     permission_classes = [IsAuthenticated]
#     serializer_class = AccommodationSerializer
#
#     def patch(self, request, *args, **kwargs):
#         """
#         호스트가 자신의 숙소 정보를 수정하는 기능
#         """
#         accommodation_id = kwargs.get('pk')
#         try:
#             accommodation = Accommodation.objects.get(id=accommodation_id, host=request.user)
#         except Accommodation.DoesNotExist:
#             return Response({"detail": "숙소를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
#
#         # 숙소 정보 수정 시 일부 필드만 수정할 수 있도록 설정
#         serializer = self.get_serializer(accommodation, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#
#         # 데이터가 유효하면 저장
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# @extend_schema(tags=["Host-Management"])
# class MyAccommodationsDeleteView(generics.GenericAPIView):
#     """숙소 삭제"""
#     permission_classes = [IsAuthenticated]
#     serializer_class = AccommodationSerializer
#
#     def delete(self, request, *args, **kwargs):
#         """
#         호스트가 자신의 숙소를 삭제하는 기능
#         """
#         accommodation_id = kwargs.get('pk')
#         try:
#             accommodation = Accommodation.objects.get(id=accommodation_id, host=request.user)
#         except Accommodation.DoesNotExist:
#             return Response({"detail": "숙소를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
#
#         accommodation.delete()
#         return Response({"detail": "숙소가 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
#
#
# @extend_schema(tags=["Host-Management"])
# class MyRoomsUpdateView(generics.GenericAPIView):
#     """객실 편집"""
#     permission_classes = [IsAuthenticated]
#     serializer_class = RoomSerializer
#     queryset = Room.objects.all()
#
#     def patch(self, request, *args, **kwargs):
#         """
#         호스트가 자신의 객실 정보를 수정하는 기능
#         """
#         room_id = kwargs.get('pk')
#         try:
#             room = Room.objects.get(id=room_id, accommodation__host=request.user)
#         except Room.DoesNotExist:
#             return Response({"detail": "객실을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
#
#         # 객실 정보 수정 시 일부 필드만 수정할 수 있도록 설정
#         serializer = self.get_serializer(room, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#
#         # 데이터가 유효하면 저장
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# @extend_schema(tags=["Host-Management"])
# class MyRoomsDeleteView(generics.GenericAPIView):
#     """객실 삭제"""
#     permission_classes = [IsAuthenticated]
#     serializer_class = RoomSerializer
#
#     def delete(self, request, *args, **kwargs):
#         """
#         호스트가 자신의 숙소 내 객실을 삭제하는 기능
#         """
#         room_id = kwargs.get('pk')
#         try:
#             room = Room.objects.get(id=room_id, accommodation__host=request.user)
#         except Room.DoesNotExist:
#             return Response({"detail": "객실을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
#
#         room.delete()
#         return Response({"detail": "객실이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)
