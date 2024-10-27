from typing import Optional

from rest_framework import serializers

from apps.pages.services.booking_total_price_service import BookingTotalPriceService
from apps.rooms.models import Room


class BookingRequestSerializer(serializers.ModelSerializer):
    accommodation_name = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    check_in_date = serializers.SerializerMethodField()
    check_out_date = serializers.SerializerMethodField()
    guests_count = serializers.SerializerMethodField()

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
        return obj.accommodation.name

    def get_total_price(self, obj: Room) -> Optional[int]:
        request = self.context.get("request")
        check_in_date = request.query_params.get("check_in_date")
        check_out_date = request.query_params.get("check_out_date")
        day_price = obj.price

        if check_in_date and check_out_date:
            price_service = BookingTotalPriceService(day_price, check_in_date, check_out_date)
            return price_service.calculate_price()

        return None

    def get_check_in_date(self, obj: Room) -> Optional[str]:
        request = self.context.get("request")
        return request.query_params.get("check_in_date")

    def get_check_out_date(self, obj: Room) -> Optional[str]:
        request = self.context.get("request")
        return request.query_params.get("check_out_date")

    def get_guests_count(self, obj: Room) -> int:
        request = self.context.get("request")
        guests_count = request.query_params.get("guests_count")
        return int(guests_count) if guests_count else 0
