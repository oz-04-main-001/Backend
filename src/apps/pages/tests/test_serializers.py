from datetime import datetime,time

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.gis.geos import Point
from rest_framework.renderers import JSONRenderer

from apps.accommodations.models import Accommodation, Accommodation_Image, GPS_Info, RefundPolicy, AccommodationType
from apps.amenities.models import Amenity, AccommodationAmenity, Option, RoomOption
from apps.pages.serializers.accommodation_serializer import AccommodationDetailSerializer, AccommodationImgSerializer
from apps.pages.serializers.main_serializer import MainPageSerializer
from apps.pages.serializers.room_serializer import RoomDetailSerializer
from apps.rooms.models import Room, Room_Image, RoomType, RoomInventory
from apps.users.models import User, BusinessUser


class AccommodationDetailSerializerTest(TestCase):
    def setUp(self):
        # 유저 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
            password="password123",
        )

        # 호스트 생성
        self.test_document = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"test document content",  # 바이너리 형태의 컨텐츠
            content_type="application/pdf",
        )
        self.host = BusinessUser.objects.create(
            user=self.user, business_document=self.test_document, business_number="123-45-67890"
        )

        # 숙소 생성
        self.accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
            is_active=True,
        )
        # 숙소 타입
        self.accommodation_type = AccommodationType.objects.create(
            accommodation=self.accommodation,
            type_name="hotel",
        )

        # 숙소 이미지
        self.accommodation_image = Accommodation_Image.objects.create(
            accommodation=self.accommodation,
            image='test_image.jpg',
            is_representative=True,
        )

        # 위치정보
        self.gps_info = GPS_Info.objects.create(
            accommodation=self.accommodation,
            city="San Francisco",
            states="CA",
            road_name="test road",
            address = "test address",
            location=Point(127.0, 37.5),
        )

        # 환불규정
        self.refund_policy = RefundPolicy.objects.create(
            accommodation=self.accommodation,
            seven_days_before = 90,
            five_days_before = 60,
            three_days_before = 30,
            one_day_before = 10,
            same_day = 0,
        )

        # Room 객체 생성
        self.room = Room.objects.create(
            accommodation=self.accommodation,
            name="Test Room",
            capacity=2,
            max_capacity=3,
            price=150,
            stay_type=True,
            description="A cozy room with amenities",
            check_in_time="15:00",
            check_out_time="11:00",
            is_available=True
        )

        # RoomType 객체 생성
        self.room_type = RoomType.objects.create(
            room=self.room,
            is_customized=True,
            type_name="Deluxe"
        )

        # Room_Image 객체 생성
        self.room_image = Room_Image.objects.create(
            room=self.room,
            image=SimpleUploadedFile(name="test_image.jpg", content=b"", content_type="image/jpeg"),
            is_representative=True
        )

        # RoomInventory 객체 생성
        self.room_inventory = RoomInventory.objects.create(
            room=self.room,
            count_room=10
        )


        # Amenity 객체 생성
        self.amenity = Amenity.objects.create(
            name="Free Wi-Fi",
            category="Connectivity",
            description="High-speed wireless internet",
            icon="wifi_icon",
            is_custom=False
        )

        # AccommodationAmenity 객체 생성
        self.accommodation_amenity = AccommodationAmenity.objects.create(
            accommodation=self.accommodation,
            amenity=self.amenity,
            custom_value=1
        )

        # Option 객체 생성
        self.option = Option.objects.create(
            name="Extra Pillow",
            category="Comfort",
            is_custom=True
        )

        # RoomOption 객체 생성
        self.room_option = RoomOption.objects.create(
            room=self.room,
            option=self.option,
            custom_value=2
        )

    # 숙박업소 상세페이지 정보 시리얼라이즈
    def test_accommodation_detail_serializer(self):
        # Serializer 인스턴스 생성
        serializer = AccommodationDetailSerializer(instance=self.accommodation)

        # 데이터 직렬화
        serialized_data = serializer.data

        # 각 필드에 대해 직렬화된 데이터가 예상대로 반환되는지 확인
        self.assertEqual(serialized_data["accommodation_info"]["name"], "Test Accommodation")
        self.assertEqual(serialized_data["address"], "San Francisco CA test road test address" )
        self.assertEqual(serialized_data["min_price"], 150)
        self.assertEqual(len(serialized_data["rooms"]), 1)
        self.assertEqual(serialized_data["rooms"][0]["name"], "Test Room")
        self.assertEqual(serialized_data["accommodation_amenity"][0]["name"], "Free Wi-Fi")
        self.assertEqual(serialized_data["refund_policy"][0]["seven_days_before"], "90.00")

    # 룸 디테일 페이지 정보 시리얼라이즈
    def test_room_detail_serializer(self):
        # RoomDetailSerializer 인스턴스 생성
        serializer = RoomDetailSerializer(instance=self.room)

        # 직렬화된 데이터 가져오기
        serialized_data = serializer.data

        # 기대되는 데이터 확인
        self.assertEqual(serialized_data["accommodation_name"], "Test Accommodation")
        self.assertEqual(serialized_data["room"]["name"], "Test Room")
        self.assertEqual(len(serialized_data["images"]), 1)
        self.assertEqual(serialized_data["room_options"][0]["name"], "Extra Pillow")

#     메인페이지 시리얼라이즈
    def test_main_page_serializer(self):
        serializer = MainPageSerializer(instance=self.accommodation)
        serialized_data = serializer.data
        representative_image_url = self.accommodation_image.image.url  # 기대하는 URL을 직접 가져옴

        self.assertEqual(serialized_data["id"], self.accommodation.id)
        self.assertEqual(serialized_data["name"], "Test Accommodation")
        self.assertEqual(serialized_data["min_price"], 150 )
        self.assertEqual(serialized_data["accommodation_img"], representative_image_url)