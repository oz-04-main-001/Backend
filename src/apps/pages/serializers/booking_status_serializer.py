from rest_framework import serializers

from apps.bookings.models import Booking
from apps.pages.serializers import room_serializer
from apps.rooms.models import Room
from apps.users.models import User
from apps.users.serializers import ui_booking_user_serializer


class BookingStatusSerializer(serializers.ModelSerializer):
    room = serializers.SerializerMethodField()
    booking_user_info = serializers.SerializerMethodField()
    class Meta:
        model = Booking
        # fields = ['check_in_date', 'check_out_date', 'total_price', 'status', 'room']
        fields = '__all__'

    def get_room(self,obj):
        room = Room.objects.get(pk=obj.room_id)
        serializer = room_serializer.RoomSerializer(room)
        return serializer.data

    def get_booking_user_info(self,obj):
        user_info = User.objects.get(pk=obj.guest_id)
        serializer = ui_booking_user_serializer.BookingUserSerializer(user_info)
        return serializer.data