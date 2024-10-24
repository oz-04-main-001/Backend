from datetime import datetime, date

from rest_framework import serializers

from apps.accommodations.models import Accommodation, Accommodation_Image
from apps.bookings.models import Booking
from apps.common.choices import BOOKING_STATUS_CHOICES
from apps.rooms.models import Room


class BookingSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source="guest.username", read_only=True)
    accommodation_name = serializers.CharField(source="room.accommodation.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "guest",
            "room",
            "check_in_datetime",
            "check_out_datetime",
            "total_price",
            "status",
            "request",
            "guests_count",
            "guest_name",
            "accommodation_name",
            "room_name",
        ]

    def validate_check_in_datetime(self, value):
        """
        체크인 날짜가 과거가 아닌지 확인
        """
        from datetime import date

        if value < date.today():
            raise serializers.ValidationError("체크인 날짜는 과거일 수 없습니다.")
        return value

    def validate_check_out_datetime(self, value):
        """
        체크아웃 날짜가 체크인 날짜 이후인지 확인
        """
        if "check_in_datetime" in self.initial_data:
            check_in_date = self.initial_data["check_in_datetime"]
            if value <= check_in_date:
                raise serializers.ValidationError("체크아웃 날짜는 체크인 날짜 이후여야 합니다.")
        return value

    def validate_total_price(self, value):
        """
        총 가격이 양수인지 확인
        """
        if value <= 0:
            raise serializers.ValidationError("총 가격은 양수여야 합니다.")
        return value

    def validate_status(self, value):
        """
        상태가 허용된 선택지 중 하나인지 확인
        """
        if value not in dict(BOOKING_STATUS_CHOICES).keys():
            raise serializers.ValidationError("유효하지 않은 예약 상태입니다.")
        return value

    def validate_guests_count(self, value):
        """
        게스트 수가 양수인지 확인
        """
        if value <= 0:
            raise serializers.ValidationError("게스트 수는 양수여야 합니다.")
        return value


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            "accommodation",
            "name",
            "capacity",
            "max_capacity",
            "price",
            "stay_type",
            "check_in_time",
            "check_out_time",
        ]

    def validate_capacity(self, value):
        """
        객실 수용 인원이 양수인지 확인
        """
        if value <= 0:
            raise serializers.ValidationError("수용 인원은 양수여야 합니다.")
        return value

    def validate_max_capacity(self, value):
        """
        최대 수용 인원이 수용 인원보다 크거나 같은지 확인
        """
        if "capacity" in self.initial_data:
            capacity = int(self.initial_data["capacity"])
            if value < capacity:
                raise serializers.ValidationError("최대 수용 인원은 수용 인원보다 크거나 같아야 합니다.")
        if value <= 0:
            raise serializers.ValidationError("최대 수용 인원은 양수여야 합니다.")
        return value

    def validate_price(self, value):
        """
        객실 가격이 양수인지 확인
        """
        if value <= 0:
            raise serializers.ValidationError("가격은 양수여야 합니다.")
        return value


class BookingCheckSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)

    def validate(self, data: dict) -> dict:
        check_date = data.get("date")
        if not check_date:
            raise serializers.ValidationError("날짜를 선택해 주세요.")

        if check_date < date.today():
            raise serializers.ValidationError("과거 날짜는 선택할 수 없습니다.")

        # 예: 너무 먼 미래의 날짜 제한
        max_future_days = 365
        if (check_date - date.today()).days > max_future_days:
            raise serializers.ValidationError(f"{max_future_days}일 이후의 날짜는 선택할 수 없습니다.")

        return data


class BookingRequestCheckSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=["accept", "cancelled"])

    def validate_booking_id(self, booking_id: int) -> int:
        try:
            booking = Booking.objects.get(id=booking_id)
            self.context["booking"] = booking
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Invalid booking ID.")
        return booking_id

    def validate_action(self, action: str) -> str:
        if action not in ["accept", "cancelled"]:
            raise serializers.ValidationError("Invalid action.")
        return action

    def validate(self, data: dict) -> dict:
        booking = self.context.get("booking")
        user = self.context.get("request").user

        if not booking:
            raise serializers.ValidationError("Booking not found.")

        if booking.status != "pending":
            raise serializers.ValidationError("This booking is not in a pending state.")

        if booking.room.accommodation.host != user.business_profile:
            raise serializers.ValidationError("You don't have permission to modify this booking.")

        return data


class BookingStatisticsSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)

    def validate_date(self, value):
        """날짜 검증 로직을 추가할 수 있습니다."""
        return value or date.today()


class AccommodationImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation_Image
        fields = ["id", "image", "image_url", "is_representative"]

    def get_image_url(self, obj):
        """이미지 URL을 반환합니다."""
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image else None


class AccommodationHostManagementSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ["id", "name", "image", "address"]

    def get_image(self, obj):
        representative_image = obj.images.filter(is_representative=True).first()
        return (
            AccommodationImageSerializer(representative_image, context=self.context).data
            if representative_image
            else None
        )

    def get_address(self, obj):
        return obj.gps_info.address if obj.gps_info else None  # GPS 정보가 없을 경우 None 반환
