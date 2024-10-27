from typing import Any, Dict

from rest_framework import serializers

from apps.bookings.models import Booking
from apps.pages.serializers import room_serializer
from apps.pages.services.convention_datetime_service import ConventionDateService
from apps.rooms.models import Room
from apps.users.models import User
from apps.users.serializers import ui_booking_user_serializer


class BookingStatusSerializer(serializers.ModelSerializer):
    room = serializers.SerializerMethodField()
    booking_user_info = serializers.SerializerMethodField()
    check_in_datetime = serializers.SerializerMethodField()
    check_out_datetime = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"

    def get_room(self, obj: Booking) -> Dict[str, Any]:
        room = Room.objects.get(pk=obj.room_id)
        serializer = room_serializer.RoomSerializer(room)
        return serializer.data

    def get_booking_user_info(self, obj: Booking) -> Dict[str, Any]:
        user_info = User.objects.get(pk=obj.guest_id)
        serializer = ui_booking_user_serializer.BookingUserSerializer(user_info)
        return serializer.data

    def get_check_in_datetime(self, obj: Booking):
        check_in_date = Booking.objects.get(id=obj.id).check_in_datetime
        check_in_datetime = ConventionDateService.format_datetime(check_in_date.isoformat())
        return check_in_datetime

    def get_check_out_datetime(self, obj: Booking):
        check_out_date = Booking.objects.get(id=obj.id).check_out_datetime
        check_out_datetime = ConventionDateService.format_datetime(check_out_date.isoformat())
        return check_out_datetime
