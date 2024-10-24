from datetime import date

from drf_spectacular.utils import extend_schema
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accommodations.models import Accommodation

from apps.bookings.models import Booking
from apps.host_management.serializers.host_management_serializers import BookingSerializer, AccommodationSerializer, \
    RoomSerializer
from apps.rooms.models import Room


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


@extend_schema(tags=["Host"])
class MyAccommodationsUpdateView(generics.GenericAPIView):
    """숙소 편집"""
    permission_classes = [IsAuthenticated]
    serializer_class = AccommodationSerializer

    def patch(self, request, *args, **kwargs):
        """
        호스트가 자신의 숙소 정보를 수정하는 기능
        """
        accommodation_id = kwargs.get('pk')
        try:
            accommodation = Accommodation.objects.get(id=accommodation_id, host=request.user)
        except Accommodation.DoesNotExist:
            return Response({"detail": "숙소를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 숙소 정보 수정 시 일부 필드만 수정할 수 있도록 설정
        serializer = self.get_serializer(accommodation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class MyAccommodationsDeleteView(generics.GenericAPIView):
    """숙소 삭제"""
    permission_classes = [IsAuthenticated]
    serializer_class = AccommodationSerializer
    queryset = Accommodation.objects.all()

    def delete(self, request, *args, **kwargs):
        """
        호스트가 자신의 숙소를 삭제하는 기능
        """
        accommodation_id = kwargs.get('pk')
        try:
            accommodation = Accommodation.objects.get(id=accommodation_id, host=request.user)
        except Accommodation.DoesNotExist:
            return Response({"detail": "숙소를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        accommodation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Host"])
class MyRoomsUpdateView(generics.GenericAPIView):
    """객실 편집"""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    def patch(self, request, *args, **kwargs):
        """
        호스트가 자신의 객실 정보를 수정하는 기능
        """
        room_id = kwargs.get('pk')
        try:
            room = Room.objects.get(id=room_id, accommodation__host=request.user)
        except Room.DoesNotExist:
            return Response({"detail": "객실을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 객실 정보 수정 시 일부 필드만 수정할 수 있도록 설정
        serializer = self.get_serializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class MyRoomsDeleteView(generics.GenericAPIView):
    """객실 삭제"""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()

    def delete(self, request, *args, **kwargs):
        """
        호스트가 자신의 숙소 내 객실을 삭제하는 기능
        """
        room_id = kwargs.get('pk')
        try:
            room = Room.objects.get(id=room_id, accommodation__host=request.user)
        except Room.DoesNotExist:
            return Response({"detail": "객실을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Host"])
class MyAccommodationListView(generics.ListAPIView):
    """숙소 내역 조회"""
    permission_classes = [IsAuthenticated]
    serializer_class = AccommodationSerializer

    def get_queryset(self):
        """
        호스트가 등록한 모든 숙소를 반환합니다.
        """
        return Accommodation.objects.filter(host=self.request.user, is_active=True)
