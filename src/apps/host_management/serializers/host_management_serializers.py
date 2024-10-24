from rest_framework import serializers

from apps.bookings.models import Booking
from apps.common.choices import BOOKING_STATUS_CHOICES
from apps.accommodations.models import Accommodation
from apps.rooms.models import Room
from apps.users.models import User


class BookingSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.username', read_only=True)
    accommodation_name = serializers.CharField(source='room.accommodation.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'guest', 'room', 'check_in_date', 'check_out_date',
            'total_price', 'status', 'request', 'guests_count',
            'guest_name', 'accommodation_name', 'room_name'
        ]

    def validate_check_in_date(self, value):
        """
        체크인 날짜가 과거가 아닌지 확인
        """
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("체크인 날짜는 과거일 수 없습니다.")
        return value

    def validate_check_out_date(self, value):
        """
        체크아웃 날짜가 체크인 날짜 이후인지 확인
        """
        if 'check_in_date' in self.initial_data:
            check_in_date = self.initial_data['check_in_date']
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


class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = [
            'host', 'name', 'phone_number', 'description', 'rules',
            'created_at', 'updated_at'
        ]

    def validate_phone_number(self, value):
        """
        전화번호가 특정 형식을 따르는지 확인
        """
        import re
        if not re.match(r"^\d{2,3}-\d{3,4}-\d{4}$", value):
            raise serializers.ValidationError("유효하지 않은 전화번호 형식입니다. 02-123-4567 또는 010-1234-5678 형식을 사용하세요.")
        return value


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'accommodation', 'name', 'capacity', 'max_capacity', 'price',
            'stay_type', 'check_in_time', 'check_out_time'
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
        if 'capacity' in self.initial_data:
            capacity = int(self.initial_data['capacity'])
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
