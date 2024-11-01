from typing import Optional

from rest_framework import serializers

from apps.pages.serializers.room_serializer import RoomSerializer
from apps.pages.services.booking_total_price_service import BookingTotalPriceService
from apps.pages.services.money_view_service import MoneyViewService
from apps.rooms.models import Room


class BookingRequestSerializer(serializers.ModelSerializer):
    accommodation_name = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    check_in_date = serializers.SerializerMethodField()
    check_out_date = serializers.SerializerMethodField()
    guests_count = serializers.SerializerMethodField()
    room_info = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["accommodation_name", "total_price", "check_in_date", "check_out_date", "guests_count", "room_info"]

    def get_accommodation_name(self, obj: Room) -> str:
        return obj.accommodation.name

    def get_total_price(self, obj: Room) -> Optional[int]:
        request = self.context.get("request")
        check_in_date = request.GET.get("check_in_date")
        check_out_date = request.GET.get("check_out_date")
        day_price = obj.price

        if check_in_date and check_out_date:
            price_service = BookingTotalPriceService(day_price, check_in_date, check_out_date)
            total_price = price_service.calculate_price()
            money_mark = MoneyViewService()
            money_total_price = money_mark.format(total_price)
            return money_total_price

        return None

    def get_check_in_date(self, obj: Room) -> Optional[str]:
        request = self.context.get("request")
        return request.GET.get("check_in_date")

    def get_check_out_date(self, obj: Room) -> Optional[str]:
        request = self.context.get("request")
        return request.GET.get("check_out_date")

    def get_guests_count(self, obj: Room) -> int:
        request = self.context.get("request")
        guests_count = request.GET.get("guests_count")
        return int(guests_count) if guests_count else 0

    def get_room_info(self, obj: Room) -> dict:
        room = Room.objects.get(id=obj.id)
        serializer = RoomSerializer(room)
        return serializer.data
