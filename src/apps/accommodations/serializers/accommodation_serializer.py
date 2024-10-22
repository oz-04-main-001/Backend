from django.contrib.gis.geos import Point
from rest_framework import serializers

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
)


class GPSInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Info
        fields = ["city", "states", "road_name", "address", "location"]

    def validate(self, data):
        """GPS 정보 유효성 검사"""
        location = data.get("location")
        if location:
            # location이 dict라면 Point 객체로 변환
            coordinates = location.get("coordinates")
            if coordinates:
                try:
                    longitude, latitude = float(coordinates[0]), float(coordinates[1])
                    if not (-90 <= latitude <= 90):
                        raise serializers.ValidationError("위도는 -90에서 90 사이의 값이어야 합니다.")
                    if not (-180 <= longitude <= 180):
                        raise serializers.ValidationError("경도는 -180에서 180 사이의 값이어야 합니다.")
                    # Point 객체로 변환
                    data["location"] = Point(longitude, latitude)
                except (TypeError, ValueError, IndexError):
                    raise serializers.ValidationError("유효한 위도와 경도 값을 입력해야 합니다.")
            else:
                raise serializers.ValidationError("좌표 정보가 필요합니다.")

        if len(data.get("city", "").strip()) < 1:
            raise serializers.ValidationError("도시명은 필수입니다.")
        if len(data.get("states", "").strip()) < 1:
            raise serializers.ValidationError("시/도는 필수입니다.")
        if len(data.get("address", "").strip()) < 5:
            raise serializers.ValidationError("주소는 최소 5자 이상이어야 합니다.")
        if len(data.get("road_name", "").strip()) < 1:
            raise serializers.ValidationError("도로명은 필수입니다.")

        return data


class AccommodationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationType
        fields = ["type_name", "is_customized"]

    def validate_type_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("숙박시설 유형은 최소 2자 이상이어야 합니다.")
        return value.strip()


class AccommodationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation_Image
        fields = ["id", "image"]

    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("이미지 크기는 10MB를 초과할 수 없습니다.")
        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("유효한 이미지 파일이 아닙니다.")
        return value


class AccommodationSerializer(serializers.ModelSerializer):
    accommodation_type = AccommodationTypeSerializer(source="accommodationtype", required=True)
    images = AccommodationImageSerializer(many=True, read_only=True)
    gps_info = GPSInfoSerializer(required=True)

    class Meta:
        model = Accommodation
        fields = [
            "id",
            "host",
            "name",
            "phone_number",
            "description",
            "rules",
            "average_rating",
            "is_active",
            "created_at",
            "updated_at",
            "accommodation_type",
            "images",
            "gps_info",
        ]
        read_only_fields = ["id", "host", "average_rating", "created_at", "updated_at"]

    def validate_phone_number(self, value):
        import re

        if not re.match(r"^\d{2,3}-\d{3,4}-\d{4}$", value):
            raise serializers.ValidationError("올바른 전화번호 형식이 아닙니다. (예: 02-123-4567 또는 010-1234-5678)")
        return value.strip()

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("숙박시설 이름은 최소 2자 이상이어야 합니다.")
        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("설명은 최소 10자 이상이어야 합니다.")
        return value.strip()

    def validate_rules(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("규칙은 최소 5자 이상이어야 합니다.")
        return value.strip()

    def create(self, validated_data):
        type_info_data = validated_data.pop("accommodationtype")
        location_info_data = validated_data.pop("gps_info")

        # 기본 숙소 생성
        accommodation = Accommodation.objects.create(**validated_data)

        # OneToOne 관계 모델 생성
        AccommodationType.objects.create(accommodation=accommodation, **type_info_data)
        GPS_Info.objects.create(accommodation=accommodation, **location_info_data)

        return accommodation

    def update(self, instance, validated_data):
        if "accommodation_type" in validated_data:
            type_info_data = validated_data.pop("accommodation_type")
            AccommodationType.objects.filter(accommodation=instance).update(**type_info_data)

        if "gps_info" in validated_data:
            location_info_data = validated_data.pop("gps_info")
            GPS_Info.objects.filter(accommodation=instance).update(**location_info_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
