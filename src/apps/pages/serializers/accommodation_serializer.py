from typing import Dict, List, Optional, Union

from rest_framework import serializers

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    GPS_Info,
    RefundPolicy,
)
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.pages.serializers.room_serializer import RoomImagesSerializer, RoomSerializer
from apps.rooms.models import Room, Room_Image


# 호텔 주소 시리얼라이저
class AccommodationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Info
        fields = [
            "city",
            "states",
            "road_name",
            "address",
        ]


# 호텔 이미지 시리얼라이저
class AccommodationImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation_Image
        fields = ["image"]


# 부대시설 시리얼라이저
class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = [
            "name",
            "category",
            "description",
            "icon",
            "is_custom",
        ]


# 호텔단위 부대시설 시리얼라이저
class AccommodationAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer()  # 부대시설 정보 포함

    class Meta:
        model = AccommodationAmenity
        fields = ["amenity"]


# 호텔 환불정책
class AccommodationRefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundPolicy
        fields = ["seven_days_before", "five_days_before", "three_days_before", "one_day_before", "same_day"]


# 호텔 기본 정보 - 이름, 전화번호, 상세내용, 이용수칙
class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ["name", "phone_number", "description", "rules"]



# ######################################
# 룸 -> 객실정보(방갯수)


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

    # 숙소 기본정보
    def get_accommodation_info(self, obj: Accommodation) -> dict:
        accommodation = Accommodation.objects.get(pk=obj.id)
        serializer = AccommodationSerializer(accommodation)
        return serializer.data

    # 숙소 이미지들
    def get_accommodation_img(self, obj: Accommodation) -> Optional[List[str]]:
        imgs = Accommodation_Image.objects.filter(accommodation_id=obj.pk)
        if imgs:
            return [img.image.url for img in imgs]
        return None

    # 숙소 주소
    def get_address(self, obj: Accommodation) -> Optional[str]:
        gps_info = GPS_Info.objects.filter(accommodation=obj)
        serializer = AccommodationAddressSerializer(gps_info, many=True)
        address_data = serializer.data[0] if serializer.data else None
        if address_data:
            return (
                f"{address_data['city']} {address_data['states']} {address_data['road_name']} {address_data['address']}"
            )
        return None

    # 최저가
    def get_min_price(self, obj: Accommodation) -> Optional[int]:
        min_price = obj.room_set.order_by("price").first()
        return min_price.price if min_price else None

    # 룸정보 + 룸대표이미지
    def get_rooms(self, obj: Accommodation) -> List[Dict[str, Union[str, Optional[str]]]]:
        rooms = Room.objects.filter(accommodation=obj)
        room_list = []

        for room in rooms:
            room_serializer = RoomSerializer(room)
            room_dict = room_serializer.data

            # 현재 room에 해당하는 이미지들을 가져옵니다.
            room_images = Room_Image.objects.filter(room_id=room.id)

            # 대표 이미지가 담길 변수
            representative_image = None

            # room에 대한 이미지를 순회하며 대표 이미지를 찾습니다.
            for image in room_images:
                if image.is_representative:
                    representative_image = image.image.url
                    break

            # 직렬화된 데이터에 'images' 필드로 대표 이미지를 추가
            room_dict["images"] = representative_image
            room_list.append(room_dict)

        return room_list

    def get_accommodation_amenity(self, obj: Accommodation) -> List[Dict[str, Union[str, bool]]]:
        accommodation_amenities = AccommodationAmenity.objects.filter(accommodation=obj)
        amenities_data = []

        for accommodation_amenity in accommodation_amenities:
            amenity = accommodation_amenity.amenity
            amenity_data = {
                "name": amenity.name,
                "category": amenity.category,
                "description": amenity.description,
                "icon": amenity.icon,
                "is_custom": amenity.is_custom,
            }
            amenities_data.append(amenity_data)

        return amenities_data

    def get_refund_policy(self, obj: Accommodation):
        refund_policy = RefundPolicy.objects.filter(accommodation=obj)
        refund_policy_serializer = AccommodationRefundPolicySerializer(refund_policy, many=True)
        return refund_policy_serializer.data


# 예약디테일에 들어갈 호텔 정보
class BookingAccommodationInfoSerializer(serializers.ModelSerializer):
    representative_image = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    class Meta:
        model = Accommodation
        fields = ['name','representative_image','address',]

    # 숙소 주소
    def get_address(self, obj: Accommodation) -> Optional[str]:
        gps_info = GPS_Info.objects.filter(accommodation=obj)
        serializer = AccommodationAddressSerializer(gps_info, many=True)
        address_data = serializer.data[0] if serializer.data else None
        if address_data:
            return (
                f"{address_data['city']} {address_data['states']} {address_data['road_name']} {address_data['address']}"
            )
        return None

    # 숙소 대표이미지
    def get_representative_image(self, obj: Accommodation) -> Optional[str]:
        img = Accommodation_Image.objects.filter(accommodation=obj, is_representative=True).first()
        if img:
            return img.image.url
        return None

