from rest_framework import serializers

from apps.bookings.models import Booking
from apps.users.serializers.ui_mypage_user_serializer import MyPageUserSerializer


class MyPageBookingSerializer(serializers.ModelSerializer):
    room_name = serializers.SerializerMethodField()
    accommodation_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "status",
            "accommodation_name",
            "room_name",
        ]

    def get_room_name(self, obj):
        return obj.room.name

    def get_accommodation_name(self, obj):
        return obj.room.accommodation.name


class MyPageSerializer(serializers.Serializer):
    login_user = serializers.SerializerMethodField()
    bookings = serializers.SerializerMethodField()

    def get_login_user(self, obj):
        user = self.context["request"].user
        return MyPageUserSerializer(user).data

    def get_bookings(self, obj):
        user = self.context["request"].user
        bookings = Booking.objects.filter(guest=user)
        return MyPageBookingSerializer(bookings, many=True).data
