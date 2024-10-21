from rest_framework import serializers
from apps.bookings.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.username', read_only=True)
    accommodation_name = serializers.CharField(source='room.accommodation.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'guest',
            'guest_name',
            'room',
            'room_name',
            'accommodation_name',
            'check_in_date',
            'check_out_date',
            'total_price',
            'status',
            'request',
        ]