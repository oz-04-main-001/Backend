from rest_framework import serializers

from apps.rooms.models import Room

# 피그마 17-숙박요청
#  룸타입 , 룸옵션, 부대시설 , 기준인원 / 침대타입,개수 / 방 개수
#  24평형 독채룸, 넷플릭스, 유튜브, 노래방
#  기준2인 / 싱금침대 1개 / 방1개

#  예약자 정보 = 로그인 유저 이름, 전화번호


class BookingRequestSerializer(serializers.ModelSerializer):
    accommodation_name = serializers.SerializerMethodField()
    room_price = serializers.SerializerMethodField()

    # bed_count =
    # room_count =
    class Meta:
        model = Room
        fields = ["accommodation_name", "name", "capacity", "check_in_time", "check_out_time", "room_price"]

    def get_accommodation_name(self, obj):
        accommodation = obj.accommodation
        return accommodation.name

    def get_room_price(self, obj):
        return obj.price
