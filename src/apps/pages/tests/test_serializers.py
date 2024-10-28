from datetime import datetime, time

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from rest_framework.renderers import JSONRenderer

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
    RefundPolicy,
)
from apps.amenities.models import AccommodationAmenity, Amenity, Option, RoomOption
from apps.bookings.models import Booking
from apps.pages.serializers.accommodation_serializer import (
    AccommodationDetailSerializer,
    AccommodationImgSerializer,
)
from apps.pages.serializers.booking_request_serializer import BookingRequestSerializer
from apps.pages.serializers.main_serializer import MainPageSerializer
from apps.pages.serializers.mypage_serializer import MyPageSerializer
from apps.pages.serializers.room_serializer import RoomDetailSerializer
from apps.pages.services.booking_total_price_service import BookingTotalPriceService
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.users.models import BusinessUser, User


class PagesSerializerTest(TestCase):
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
            image="test_image.jpg",
            is_representative=True,
        )

        # 위치정보
        self.gps_info = GPS_Info.objects.create(
            accommodation=self.accommodation,
            city="San Francisco",
            states="CA",
            road_name="test road",
            address="test address",
            location=Point(127.0, 37.5),
        )

        # 환불규정
        self.refund_policy = RefundPolicy.objects.create(
            accommodation=self.accommodation,
            seven_days_before=90,
            five_days_before=60,
            three_days_before=30,
            one_day_before=10,
            same_day=0,
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
            is_available=True,
        )

        # RoomType 객체 생성
        self.room_type = RoomType.objects.create(room=self.room, is_customized=True, type_name="Deluxe")

        # Room_Image 객체 생성
        self.room_image = Room_Image.objects.create(
            room=self.room,
            image=SimpleUploadedFile(name="test_image.jpg", content=b"", content_type="image/jpeg"),
            is_representative=True,
        )

        # RoomInventory 객체 생성
        self.room_inventory = RoomInventory.objects.create(room=self.room, count_room=10)

        # Amenity 객체 생성
        self.amenity = Amenity.objects.create(
            name="Free Wi-Fi",
            category="Connectivity",
            description="High-speed wireless internet",
            icon="wifi_icon",
            is_custom=False,
        )

        # AccommodationAmenity 객체 생성
        self.accommodation_amenity = AccommodationAmenity.objects.create(
            accommodation=self.accommodation, amenity=self.amenity, custom_value=1
        )

        # Option 객체 생성
        self.option = Option.objects.create(name="Extra Pillow", category="Comfort", is_custom=True)

        # RoomOption 객체 생성
        self.room_option = RoomOption.objects.create(room=self.room, option=self.option, custom_value=2)

        # 예약 생성
        self.booking = Booking.objects.create(
            guest=self.user,  # 수정된 부분
            room=self.room,
            check_in_datetime=datetime(2023, 10, 1, 15, 0),  # 수정된 부분
            check_out_datetime=datetime(2023, 10, 5, 11, 0),  # 수정된 부분
            total_price=600,  # 예시로 설정한 총 가격
            status="confirmed",
            request="Extra towels requested.",
            guests_count=2,
            booker_name="John Doe",
            booker_phone_number="010-1234-5678",
        )

        # 로그인
        self.client.login(email="test_user@example.com", password="password123")

        # RequestFactory instance to simulate HTTP requests
        self.factory = RequestFactory()

    # 숙박업소 상세페이지 정보 시리얼라이즈 테스트
    def test_accommodation_detail_serializer(self):
        # Serializer 인스턴스 생성
        serializer = AccommodationDetailSerializer(instance=self.accommodation)

        # 데이터 직렬화
        serialized_data = serializer.data

        # 각 필드에 대해 직렬화된 데이터가 예상대로 반환되는지 확인
        self.assertEqual(serialized_data["accommodation_info"]["name"], "Test Accommodation")
        self.assertEqual(serialized_data["address"], "San Francisco CA test road test address")
        self.assertEqual(serialized_data["min_price"], 150)
        self.assertEqual(len(serialized_data["rooms"]), 1)
        self.assertEqual(serialized_data["rooms"][0]["name"], "Test Room")
        self.assertEqual(serialized_data["accommodation_amenity"][0]["name"], "Free Wi-Fi")
        self.assertEqual(serialized_data["refund_policy"][0]["seven_days_before"], "90.00")

    # 룸 디테일 페이지 정보 시리얼라이즈 테스트
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

    # 메인페이지 시리얼라이즈 테스트
    def test_main_page_serializer(self):
        serializer = MainPageSerializer(instance=self.accommodation)
        serialized_data = serializer.data
        representative_image_url = self.accommodation_image.image.url  # 기대하는 URL을 직접 가져옴

        self.assertEqual(serialized_data["id"], self.accommodation.id)
        self.assertEqual(serialized_data["name"], "Test Accommodation")
        self.assertEqual(serialized_data["min_price"], 150)
        self.assertEqual(serialized_data["accommodation_img"], representative_image_url)

    # 로그인한 사용자 정보와 그 사용자의 예약목록이 올바르게 직렬화 되는지 검증합니다.
    def test_my_page_serializer(self):
        # RequestFactory를 통해 요청 생성
        factory = self.factory
        request = factory.get("/fake-url/")
        request.user = self.user  # 로그인한 사용자 설정

        # Serializer 인스턴스 생성, context에 request 추가
        serializer = MyPageSerializer(instance=self.user, context={"request": request})
        serialized_data = serializer.data

        # 로그인 사용자 정보 확인
        self.assertEqual(serialized_data["login_user"]["email"], "test@example.com")

        # 예약 정보 확인
        self.assertEqual(len(serialized_data["bookings"]), 1)
        self.assertEqual(serialized_data["bookings"][0]["room_name"], "Test Room")
        self.assertEqual(serialized_data["bookings"][0]["accommodation_name"], "Test Accommodation")
        self.assertEqual(serialized_data["bookings"][0]["accommodation_img"], self.accommodation_image.image.url)

    # 유효한 체크인 날자, 체크아웃 날자, 손님 수를 포함한 요청을 만들어, 직렬화 된 데이터가 예상되는 값들과 일치하는지 확인
    def test_booking_request_serializer_with_valid_data(self):
        # 유효한 데이터로 요청을 생성합니다.
        request = self.factory.get(
            "/fake-url/", {"check_in_date": "2023-10-01", "check_out_date": "2023-10-05", "guests_count": "2"}
        )

        # BookingRequestSerializer 인스턴스를 생성합니다.
        serializer = BookingRequestSerializer(instance=self.room, context={"request": request})
        serialized_data = serializer.data

        # 요청에서 체크인 및 체크아웃 날짜를 가져옵니다.
        check_in_date = request.GET["check_in_date"]  # 수정된 부분
        check_out_date = request.GET["check_out_date"]  # 수정된 부분

        # 객실 가격을 가져와서 예상 총 가격을 계산합니다.
        day_price = self.room.price
        expected_total_price = BookingTotalPriceService(day_price, check_in_date, check_out_date).calculate_price()

        # 직렬화된 데이터가 예상과 일치하는지 검증합니다.
        self.assertEqual(serialized_data["accommodation_name"], self.room.accommodation.name)  # 숙소 이름 확인
        self.assertEqual(serialized_data["check_in_date"], check_in_date)  # 체크인 날짜 확인
        self.assertEqual(serialized_data["check_out_date"], check_out_date)  # 체크아웃 날짜 확인
        self.assertEqual(serialized_data["guests_count"], 2)  # 손님 수 확인
        self.assertEqual(serialized_data["total_price"], expected_total_price)  # 총 가격 확인

    # 체크인 및 체크아웃 날짜 없이 요청을 만들어, 총 가격이 None으로 반환되는지 확인
    def test_booking_request_serializer_with_missing_dates(self):
        # 체크인 및 체크아웃 날짜가 없는 요청을 생성합니다.
        request = self.factory.get("/fake-url/", {"guests_count": "2"})

        # BookingRequestSerializer 인스턴스를 생성합니다.
        serializer = BookingRequestSerializer(instance=self.room, context={"request": request})
        serialized_data = serializer.data

        # 총 가격이 None인지 검증합니다.
        self.assertIsNone(serialized_data["total_price"])  # 총 가격 확인

    # 유효하지 않은 손님 수를 포함한 요청을 만들어, 데이터 직렬화 과정에서 ValueError가 발생하는지 확인
    def test_booking_request_serializer_with_invalid_guests_count(self):
        # 유효하지 않은 손님 수로 요청을 생성합니다.
        request = self.factory.get(
            "/fake-url/", {"check_in_date": "2023-10-01", "check_out_date": "2023-10-05", "guests_count": "invalid"}
        )

        # ValueError가 발생하는지 검증합니다.
        with self.assertRaises(ValueError):
            serializer = BookingRequestSerializer(instance=self.room, context={"request": request})
            serializer.data  # 데이터 직렬화 시도

        # 부킹 요청을 할 때 고객이 선택한 날짜와 호텔 및 룸 정보를 가져오는지 테스트
        def test_booking_request_serializer_with_valid_data(self):
            # 유효한 데이터로 요청을 생성합니다.
            request = self.factory.get(
                "/fake-url/", {"check_in_date": "2023-10-01", "check_out_date": "2023-10-05", "guests_count": "2"}
            )

            # BookingRequestSerializer 인스턴스를 생성합니다.
            serializer = BookingRequestSerializer(instance=self.room, context={"request": request})
            serialized_data = serializer.data

            # 요청에서 체크인 및 체크아웃 날짜를 가져옵니다.
            check_in_date = request.GET["check_in_date"]
            check_out_date = request.GET["check_out_date"]

            # 객실 가격을 가져와서 예상 총 가격을 계산합니다.
            day_price = self.room.price
            expected_total_price = BookingTotalPriceService(day_price, check_in_date, check_out_date).calculate_price()

            # 직렬화된 데이터가 예상과 일치하는지 검증합니다.
            self.assertEqual(serialized_data["accommodation_name"], self.room.accommodation.name)  # 숙소 이름 확인
            self.assertEqual(serialized_data["check_in_date"], check_in_date)  # 체크인 날짜 확인
            self.assertEqual(serialized_data["check_out_date"], check_out_date)  # 체크아웃 날짜 확인
            self.assertEqual(serialized_data["guests_count"], 2)  # 손님 수 확인
            self.assertEqual(serialized_data["total_price"], expected_total_price)  # 총 가격 확인

        def test_booking_request_serializer_with_missing_dates(self):
            # 체크인 및 체크아웃 날짜가 없는 요청을 생성합니다.
            request = self.factory.get("/fake-url/", {"guests_count": "2"})

            # BookingRequestSerializer 인스턴스를 생성합니다.
            serializer = BookingRequestSerializer(instance=self.room, context={"request": request})
            serialized_data = serializer.data

            # 총 가격이 None인지 검증합니다.
            self.assertIsNone(serialized_data["total_price"])  # 총 가격 확인

        def test_booking_request_serializer_with_invalid_guests_count(self):
            # 유효하지 않은 손님 수로 요청을 생성합니다.
            request = self.factory.get(
                "/fake-url/", {"check_in_date": "2023-10-01", "check_out_date": "2023-10-05", "guests_count": "invalid"}
            )

            # ValueError가 발생하는지 검증합니다.
            with self.assertRaises(ValueError):
                serializer = BookingRequestSerializer(instance=self.room, context={"request": request})
                serializer.data  # 데이터 직렬화 시도

        # 부킹 요청을 할 때 고객이 선택한 날자를 잘 가져오는지 테스트
        def test_booking_request_serializer_with_dates(self):
            # 유효한 데이터로 요청을 생성합니다.
            request = self.factory.get(
                "/fake-url/", {"check_in_date": "2023-10-01", "check_out_date": "2023-10-05", "guests_count": "2"}
            )

            # BookingRequestSerializer 인스턴스를 생성합니다.
            serializer = BookingRequestSerializer(instance=self.room, context={"request": request})
            serialized_data = serializer.data

            # 직렬화된 데이터에서 체크인 날짜 및 체크아웃 날짜가 올바르게 반환되는지 확인
            self.assertEqual(serialized_data["check_in_date"], "2023-10-01")  # 체크인 날짜 확인
            self.assertEqual(serialized_data["check_out_date"], "2023-10-05")  # 체크아웃 날짜 확인
            self.assertEqual(serialized_data["guests_count"], 2)  # 손님 수 확인
            self.assertEqual(serialized_data["accommodation_name"], self.room.accommodation.name)  # 숙소 이름 확인
