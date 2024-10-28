from rest_framework import serializers

from apps.accommodations.models import Accommodation
from apps.rooms.models import Room


class AccommodationAvailabilityRequestSerializer(serializers.Serializer):
    state = serializers.CharField(required=True, max_length=100)
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    guests_count = serializers.IntegerField(required=True, min_value=1)

    def validate(self, data):
        # 체크아웃 날짜가 체크인 날짜보다 빠른 경우 에러 처리
        if data["check_out_date"] <= data["check_in_date"]:
            raise serializers.ValidationError("체크아웃 날짜는 체크인 날짜보다 늦어야 합니다.")
        return data


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "capacity", "max_capacity", "price", "is_available"]


class AccommodationAvailabilityResponseSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)  # 예약 가능한 방 목록 포함

    class Meta:
        model = Accommodation
        fields = ["id", "name", "phone_number", "description", "average_rating", "is_active", "rooms"]
