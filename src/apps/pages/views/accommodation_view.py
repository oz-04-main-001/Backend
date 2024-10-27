from typing import Dict, List, Optional, Union

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    GPS_Info,
    RefundPolicy,
)
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.pages.serializers.room_serializer import RoomSerializer
from apps.rooms.models import Room, Room_Image


# 호텔 주소 시리얼라이저
class AccommodationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Info
        fields = ["city", "states", "road_name", "address"]


# 호텔 이미지 시리얼라이저
class AccommodationImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation_Image
        fields = ["image"]


# 부대시설 시리얼라이저
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["name", "category", "description", "icon", "is_custom"]


# 호텔 단위 부대시설 시리얼라이저
class AccommodationAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer()

    class Meta:
        model = AccommodationAmenity
        fields = ["amenity"]


# 환불 정책 시리얼라이저
class AccommodationRefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundPolicy
        fields = ["seven_days_before", "five_days_before", "three_days_before", "one_day_before", "same_day"]


# 호텔 기본 정보 시리얼라이저
class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ["name", "phone_number", "description", "rules"]


# 호텔 상세 정보 시리얼라이저
class AccommodationDetailSerializer(serializers.ModelSerializer):
    accommodation_info = serializers.SerializerMethodField()
    accommodation_img = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    refund_policy = serializers.SerializerMethodField()
    accommodation_amenity = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = [
            "accommodation_img",
            "accommodation_info",
            "address",
            "min_price",
            "rooms",
            "accommodation_amenity",
            "refund_policy",
        ]

    def get_accommodation_info(self, obj: Accommodation) -> dict:
        return AccommodationSerializer(obj).data

    def get_accommodation_img(self, obj: Accommodation) -> Optional[List[str]]:
        imgs = Accommodation_Image.objects.filter(accommodation_id=obj.pk)
        return [img.image.url for img in imgs] if imgs else None

    def get_address(self, obj: Accommodation) -> Optional[str]:
        gps_info = GPS_Info.objects.filter(accommodation=obj).first()
        if gps_info:
            return f"{gps_info.city} {gps_info.states} {gps_info.road_name} {gps_info.address}"
        return None

    def get_min_price(self, obj: Accommodation) -> Optional[int]:
        min_room = obj.room_set.order_by("price").first()
        return min_room.price if min_room else None

    def get_rooms(self, obj: Accommodation) -> List[Dict[str, Union[str, Optional[str]]]]:
        rooms = Room.objects.filter(accommodation=obj)
        room_list = []

        for room in rooms:
            room_serializer = RoomSerializer(room)
            room_data = room_serializer.data

            representative_image = Room_Image.objects.filter(room_id=room.id, is_representative=True).first()
            room_data["images"] = representative_image.image.url if representative_image else None
            room_list.append(room_data)

        return room_list

    def get_accommodation_amenity(self, obj: Accommodation) -> List[dict]:
        amenities = AccommodationAmenity.objects.filter(accommodation=obj)
        return AccommodationAmenitySerializer(amenities, many=True).data

    def get_refund_policy(self, obj: Accommodation) -> List[dict]:
        refund_policy = RefundPolicy.objects.filter(accommodation=obj)
        return AccommodationRefundPolicySerializer(refund_policy, many=True).data


# 숙박 업소 디테일 뷰
@extend_schema(tags=["Guest"])
class AccommodationDetailView(RetrieveAPIView):
    serializer_class = AccommodationDetailSerializer
    permission_classes = (AllowAny,)
    queryset = Accommodation.objects.all()

    @extend_schema(
        summary="숙박 업소 디테일",
        description="capacity: 기준 인원 / max_capacity: 최대 인원",
        responses={200: AccommodationDetailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
