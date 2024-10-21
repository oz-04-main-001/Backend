from rest_framework import serializers
from apps.bookings.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.username', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'check_in_date',
            'check_out_date',
            'total_price',
            'status',
            'guest_id',
            'room_id',
            'guest_name',
        ]