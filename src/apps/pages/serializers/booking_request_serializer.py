from datetime import datetime
from typing import Optional

from rest_framework import serializers

from apps.pages.services.booking_total_price_service import BookingTotalPriceService
from apps.rooms.models import Room

# 피그마 17-숙박요청
#  룸타입 , 룸옵션, 부대시설 , 기준인원 / 침대타입,개수 / 방 개수
#  24평형 독채룸, 넷플릭스, 유튜브, 노래방
#  기준2인 / 싱금침대 1개 / 방1개

#  예약자 정보 = 로그인 유저 이름, 전화번호


class BookingRequestSerializer(serializers.ModelSerializer):
    accommodation_name = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    check_in_date = serializers.SerializerMethodField()
    check_out_date = serializers.SerializerMethodField()
    guests_count = serializers.SerializerMethodField()

    # bed_count =
    # room_count =
    class Meta:
        model = Room
        fields = [
            "accommodation_name",
            "check_in_date",
            "check_out_date",
            "guests_count",
            "name",
            "capacity",
            "check_in_time",
            "check_out_time",
            "total_price",
        ]

    def get_accommodation_name(self, obj: Room) -> str:
        accommodation = obj.accommodation
        return accommodation.name

    def get_total_price(self, obj: Room) -> Optional[int]:
        # 프론트에서 체크인,체크아웃날자를 받아옴
        request = self.context.get("request")
        check_in_date = request.query_params.get("check_in_date")
        check_out_date = request.query_params.get("check_out_date")
        day_price = obj.price

        if check_in_date and check_out_date:
            price_service = BookingTotalPriceService(day_price, check_in_date, check_out_date)
            total_price = price_service.calculate_price()
            return total_price

        return None

    def get_check_in_date(self, obj: Room) -> Optional[datetime]:
        request = self.context.get("request")
        check_in_date = request.query_params.get("check_in_date", None)
        if check_in_date:
            return check_in_date
        return None

    def get_check_out_date(self, obj: Room) -> Optional[datetime]:
        request = self.context.get("request")
        check_out_date = request.query_params.get("check_out_date", None)
        if check_out_date:
            return check_out_date
        return None

    def get_guests_count(self, obj: Room) -> int:
        request = self.context.get("request")
        guests_count = request.query_params.get("guests_count", None)
        if guests_count:
            return guests_count
        return 0
