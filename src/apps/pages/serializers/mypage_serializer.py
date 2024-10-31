from typing import Any, Dict, List

from rest_framework import serializers

from apps.accommodations.models import Accommodation_Image
from apps.bookings.models import Booking
from apps.users.serializers.ui_mypage_user_serializer import MyPageUserSerializer


class MyPageBookingSerializer(serializers.ModelSerializer):
    room_name = serializers.SerializerMethodField()
    accommodation_name = serializers.SerializerMethodField()
    accommodation_img = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "accommodation_img",
            "id",
            "status",
            "accommodation_name",
            "room_name",
        ]

    def get_accommodation_img(self, obj: Booking) -> str:
        # Accommodation_Image의 첫 번째 이미지를 반환
        accommodation_image = Accommodation_Image.objects.filter(accommodation=obj.room.accommodation).first()
        return accommodation_image.image.url if accommodation_image else None

    def get_room_name(self, obj: Booking) -> str:
        return obj.room.name

    def get_accommodation_name(self, obj: Booking) -> str:
        return obj.room.accommodation.name


class MyPageSerializer(serializers.Serializer):
    login_user = serializers.SerializerMethodField()
    bookings = serializers.SerializerMethodField()

    def get_login_user(self, obj: Any) -> Dict[str, Any]:
        user = self.context["request"].user
        return MyPageUserSerializer(user).data

    def get_bookings(self, obj: Any):
        user = self.context["request"].user
        bookings = Booking.objects.filter(guest=user)
        return MyPageBookingSerializer(bookings, many=True).data
