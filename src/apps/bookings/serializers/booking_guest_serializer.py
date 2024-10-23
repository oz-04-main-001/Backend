import re
from datetime import date

from rest_framework import serializers

from apps.bookings.models import Booking
from apps.bookings.services.booking_guest_service import BookingService
from apps.rooms.models import Room


class BookingReqeustCreateSerializer(serializers.ModelSerializer):
    accommodation_id = serializers.IntegerField()
    room_id = serializers.IntegerField()
    booker_phone_number = serializers.CharField()
    booker_name = serializers.CharField()

    class Meta:
        model = Booking
        fields = [
            "check_in_date",
            "check_out_date",
            "guests_count",
            "booker_name",
            "booker_phone_number",
            "accommodation_id",
            "room_id",
        ]

    def validate_booker_phone_number(self, value: str) -> str:
        phone_regex = re.compile(r"^010-\d{4}-\d{4}$")
        if not phone_regex.match(value):
            raise serializers.ValidationError("Phone number must be in the format 010-1234-5678.")
        return value

    def validate(self, data: dict) -> dict:
        room_id = data["room_id"]
        guests_count = data["guests_count"]
        check_in_date = data["check_in_date"]
        check_out_date = data["check_out_date"]

        try:
            room = Room.objects.get_by_room_id(room_id=room_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room does not exist.")

        if not room.is_available:
            raise serializers.ValidationError("This room is not available.")

        if guests_count < room.capacity or guests_count > room.max_capacity:
            raise serializers.ValidationError(f"Guests count must be between {room.capacity} and {room.max_capacity}.")

        if check_in_date >= check_out_date:
            raise serializers.ValidationError("Check-out date must be after check-in date.")

        if check_in_date < date.today():
            raise serializers.ValidationError("Check-in date cannot be in the past.")

        overlapping_bookings = BookingService.check_overlapping_bookings(room, check_in_date, check_out_date)

        if room.roominventory.count_room < overlapping_bookings + 1:
            raise serializers.ValidationError("No rooms available for the selected dates.")

        max_booking_days = 30

        if (check_out_date - check_in_date).days > max_booking_days:
            raise serializers.ValidationError(f"Booking duration cannot exceed {max_booking_days} days.")

        max_future_days = 365
        if (check_in_date - date.today()).days > max_future_days:
            raise serializers.ValidationError(f"Bookings can only be made up to {max_future_days} days in advance.")

        total_price = room.price * (check_out_date - check_in_date).days

        data["total_price"] = total_price

        return data


class BookingCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "status"]
        read_only_fields = ["id"]
