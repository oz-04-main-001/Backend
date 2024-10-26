from rest_framework import serializers

from apps.accommodations.models import Accommodation, Accommodation_Image
from apps.bookings.models import Booking
from apps.pages.serializers.accommodation_serializer import AccommodationImgSerializer
from apps.rooms.models import Room
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

    def get_accommodation_img(self, obj):
        # Accommodation_Image의 첫 번째 이미지를 사용하거나 필요에 따라 조정 가능
        accommodation_image = Accommodation_Image.objects.filter(accommodation=obj.room.accommodation).first()
        if accommodation_image:
            return accommodation_image.image.url
        return None

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
