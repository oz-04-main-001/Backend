from rest_framework import serializers, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from apps.pages.serializers.booking_request_serializer import BookingRequestSerializer
from apps.rooms.models import Room

class BookingRequestView(RetrieveAPIView):
    serializer_class = BookingRequestSerializer

    def get_queryset(self):
        accommodation = self.kwargs["accommodation_pk"]
        return Room.objects.filter(accommodation__id=accommodation)

    def get(self, request, *args, **kwargs):
        check_in_date = request.GET.get("check_in_date")
        check_out_date = request.GET.get("check_out_date")

        # 날짜 형식 검사
        if not self.is_valid_date(check_in_date) or not self.is_valid_date(check_out_date):
            return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            # 예외가 발생했을 때 로그에 출력하고 500 오류를 반환
            print(f"Error occurred: {str(e)}")  # 또는 logging 모듈 사용
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def is_valid_date(self, date_str):
        if date_str:
            date = parse_date(date_str)
            return date is not None
        return False
