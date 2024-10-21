from rest_framework import serializers

from apps.bookings.models import Booking


class BookingReqeustCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["id"]


class BookingCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "status"]
        read_only_fields = ["id"]
