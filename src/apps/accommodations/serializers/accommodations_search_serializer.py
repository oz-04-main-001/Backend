from django.db.models import Min
from rest_framework import serializers

from apps.accommodations.models import Accommodation
from apps.common.choices import STATE_CHOICES


class AccommodationAvailabilityRequestSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=STATE_CHOICES)
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    guests_count = serializers.IntegerField(required=True, min_value=1)

    def validate(self, data):
        # 체크아웃 날짜가 체크인 날짜보다 빠른 경우 에러 처리
        if data["check_out_date"] <= data["check_in_date"]:
            raise serializers.ValidationError("체크아웃 날짜는 체크인 날짜보다 늦어야 합니다.")
        return data


class AccommodationAvailabilityResponseSerializer(serializers.ModelSerializer):
    room = serializers.SerializerMethodField()
    lowest_price = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    representative_image = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = [
            "id",
            "name",
            "lowest_price",
            "location",
            "representative_image",
            "room",
        ]

    def get_room(self, obj):
        # room_set을 사용하여 Room의 ID 리스트 반환
        return list(obj.room_set.values_list("id", flat=True))

    def get_lowest_price(self, obj):
        # room_set으로 최저 가격을 계산
        return obj.room_set.aggregate(lowest_price=Min("price"))["lowest_price"]

    def get_location(self, obj):
        if obj.gps_info and obj.gps_info.location:
            return (obj.gps_info.location.y, obj.gps_info.location.x)
        return None

    def get_representative_image(self, obj):
        image = obj.images.filter(is_representative=True).first()
        return image.image.url if image else None
