from rest_framework import serializers

from apps.bookings.models import Booking


class BookingReqeustCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id']

    def create(self, validated_data):
        instance = Booking(**validated_data)
        instance.save()
        return instance


class BookingCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id','status']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        # 예약 상태를 취소로 설정
        instance.status = 'cancelled_by_guest'
        instance.save()
        return instance
