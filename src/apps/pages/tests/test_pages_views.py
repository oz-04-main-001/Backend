from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.accommodations.models import Accommodation, Accommodation_Image
from apps.bookings.models import Booking
from apps.rooms.models import Room
from apps.users.models import BusinessUser, User


class AccommodationDetailViewTest(APITestCase):
    def setUp(self):
        # 유저 및 비즈니스 유저 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
            password="password123",
        )
        self.host = BusinessUser.objects.create(user=self.user, business_number="123-45-67890")

        # 숙박업소 생성
        self.accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
            is_active=True,
        )

        # URL 및 기본 데이터 설정
        self.url = reverse("pages:accommodation_detail", args=[self.accommodation.id])
        self.valid_data = {
            "check_in_date": "2029-10-01",  # 날짜만 포함
            "check_out_date": "2029-10-05",  # 날짜만 포함
            "guests_count": 2,
        }

    def test_accommodation_detail_view_with_valid_data(self):
        # 로그인한 사용자로 요청
        self.client.login(email="test@example.com", password="password123")

        # URL에 쿼리 파라미터를 포함하여 요청
        response = self.client.get(
            self.url,
            {
                "check_in_date": self.valid_data["check_in_date"],
                "check_out_date": self.valid_data["check_out_date"],
                "guests_count": self.valid_data["guests_count"],
            },
        )

        # 응답 상태 코드 및 데이터 출력
        print("Response status code:", response.status_code)
        print("Response data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터가 올바르게 직렬화되었는지 확인
        data = response.json()
        self.assertEqual(data["accommodation"]["accommodation_info"]["name"], "Test Accommodation")
        self.assertEqual(data["accommodation"]["accommodation_info"]["phone_number"], "02-1234-5678")
        self.assertIn("available_rooms", data)  # available_rooms가 있는지 확인
        self.assertIn("unavailable_rooms", data)  # unavailable_rooms가 있는지 확인

    def test_accommodation_detail_view_with_missing_data(self):
        # 로그인한 사용자로 요청
        self.client.login(email="test@example.com", password="password123")

        # 유효하지 않은 (필수 인자 누락) 데이터로 요청
        response = self.client.get(self.url, {"check_in_date": "2023-10-01"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accommodation_detail_view_with_invalid_date_format(self):
        # 로그인한 사용자로 요청
        self.client.login(email="test@example.com", password="password123")

        # 잘못된 날짜 형식으로 요청
        invalid_data = self.valid_data.copy()
        invalid_data["check_in_date"] = "01-10-2023"  # 잘못된 형식
        response = self.client.get(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accommodation_detail_view_with_insufficient_guest_count(self):
        # 로그인한 사용자로 요청
        self.client.login(email="test@example.com", password="password123")

        # 손님 수가 0명일 때의 요청
        invalid_data = self.valid_data.copy()
        invalid_data["guests_count"] = 0
        response = self.client.get(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RoomDetailViewTest(APITestCase):
    def setUp(self):
        # 유저 및 비즈니스 유저 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
            password="password123",
        )
        self.host = BusinessUser.objects.create(user=self.user, business_number="123-45-67890")

        # 숙박업소 생성
        self.accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
            is_active=True,
        )

        # 방 생성
        self.room = Room.objects.create(
            accommodation=self.accommodation,
            name="Test Room",
            capacity=2,
            max_capacity=4,
            price=100.00,
            stay_type=True,
            description="Test Room Description",
            check_in_time="14:00:00",
            check_out_time="12:00:00",
        )

        # URL 설정
        self.url = reverse("pages:room_detail", args=[self.accommodation.id, self.room.id])

    def test_room_detail_view(self):
        # 로그인한 사용자로 요청
        self.client.login(email="test@example.com", password="password123")

        # 방 디테일 요청
        response = self.client.get(self.url)

        # 응답 상태 코드 및 데이터 출력
        print("Response status code:", response.status_code)
        print("Response data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터가 올바르게 직렬화되었는지 확인
        data = response.json()
        self.assertEqual(data["room"]["name"], "Test Room")
        self.assertEqual(data["room"]["capacity"], 2)
        self.assertEqual(data["room"]["max_capacity"], 4)
        self.assertEqual(data["room"]["price"], "100")
        self.assertEqual(data["room"]["description"], "Test Room Description")
        self.assertEqual(data["room"]["check_in_time"], "14:00:00")
        self.assertEqual(data["room"]["check_out_time"], "12:00:00")

    def test_room_detail_view_without_login(self):
        # 로그인하지 않고 요청
        response = self.client.get(self.url)

        # 응답 상태 코드 및 데이터 출력
        print("Response status code (without login):", response.status_code)

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # AllowAny로 설정된 경우


class MainListViewTest(APITestCase):
    def setUp(self):
        # 유저 및 비즈니스 유저 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
            password="password123",
        )
        self.host = BusinessUser.objects.create(user=self.user, business_number="123-45-67890")

        # 숙소 생성
        self.accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
            is_active=True,
        )

        # 숙소 이미지 생성 (대표 이미지)
        Accommodation_Image.objects.create(
            accommodation=self.accommodation,
            image="path/to/image.jpg",  # 실제 파일 경로로 대체해야 함
            is_representative=True,
        )

        # URL 설정
        self.url = reverse("pages:main_list")  # 실제 URL 이름으로 대체해야 함

    def test_main_list_view_accessible_without_login(self):
        # 로그인하지 않고 메인 리스트 요청
        response = self.client.get(self.url)

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_main_list_view_response_data(self):
        # 로그인하지 않고 메인 리스트 요청
        response = self.client.get(self.url)

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        data = response.json()
        self.assertIsInstance(data, list)  # 데이터 형식이 리스트인지 확인
        self.assertGreater(len(data), 0)  # 숙소 데이터가 포함되어 있는지 확인

        # 첫 번째 숙소 데이터 확인
        accommodation_data = data[0]
        self.assertEqual(accommodation_data["name"], "Test Accommodation")
        self.assertIn("min_price", accommodation_data)  # min_price 필드 확인
        self.assertIn("accommodation_img", accommodation_data)  # accommodation_img 필드 확인

    def test_main_list_view_no_accommodations(self):
        # 기존 숙소 삭제
        Accommodation.objects.all().delete()

        # 로그인하지 않고 메인 리스트 요청
        response = self.client.get(self.url)

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인 (빈 리스트)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)  # 숙소 데이터가 없을 때 빈 리스트 확인


# MyPageView
class MyBookingListViewTest(APITestCase):
    def setUp(self):
        # 유저 및 비즈니스 유저 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
        )
        self.host = BusinessUser.objects.create(user=self.user, business_number="123-45-67890")

        # 숙박업소 생성
        self.accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
            is_active=True,
        )

        # 방 생성
        self.room = Room.objects.create(
            accommodation=self.accommodation,
            name="Test Room",
            capacity=2,
            max_capacity=4,
            price=100.00,
            stay_type=True,
            description="Test Room Description",
            check_in_time="14:00:00",
            check_out_time="12:00:00",
        )

        # 체크인 및 체크아웃 날짜 설정
        self.check_in_datetime = timezone.now() + timedelta(days=1)  # 내일 체크인
        self.check_out_datetime = self.check_in_datetime + timedelta(days=2)  # 2일 후 체크아웃

        # 예약 생성 (필수 필드 모두 포함)
        self.booking = Booking.objects.create(
            guest=self.user,
            room=self.room,
            check_in_datetime=self.check_in_datetime,
            check_out_datetime=self.check_out_datetime,
            total_price=self.room.price,  # 방의 가격을 total_price에 설정
            status="confirmed",  # 예약 상태
            booker_name=self.user.first_name + " " + self.user.last_name,  # 예약자 이름
            booker_phone_number=self.user.phone_number,  # 예약자 전화번호
        )

        # 숙소 이미지 생성
        Accommodation_Image.objects.create(
            accommodation=self.accommodation,
            image="http://example.com/image.jpg",
            is_representative=True,
        )

        # URL 설정
        self.url = reverse("pages:my_booking_list")

        # APIClient 생성
        self.client = APIClient()

        # 사용자 로그인
        login_successful = self.client.login(email="test@example.com", password="password123")
        print("Login successful:", login_successful)  # 로그인 성공 여부 확인


def test_my_booking_list_view_with_authenticated_user(self):
    # 예약 목록 요청
    response = self.client.get(self.url)

    # 응답 상태 코드 확인
    print("Response status code:", response.status_code)  # 응답 코드 출력
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 응답 데이터 확인
    data = response.json()
    self.assertIsInstance(data, dict)  # 데이터 형식이 dict인지 확인
    self.assertIn("login_user", data)  # 로그인 사용자 정보 확인
    self.assertIn("bookings", data)  # 예약 목록 확인
    self.assertEqual(len(data["bookings"]), 1)  # 예약 개수 확인

    # 첫 번째 예약 데이터 확인
    booking_data = data["bookings"][0]
    self.assertEqual(booking_data["id"], self.booking.id)
    self.assertEqual(booking_data["room_name"], "Test Room")
    self.assertEqual(booking_data["accommodation_name"], "Test Accommodation")
    self.assertEqual(booking_data["status"], "confirmed")
    self.assertEqual(booking_data["accommodation_img"], "http://example.com/image.jpg")


def test_my_booking_list_view_without_login(self):
    # 사용자가 로그아웃 상태에서 요청합니다.
    self.client.logout()  # 로그아웃
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # 인증되지 않은 경우


# booking_request_view 테스트 코드
class BookingRequestViewTest(APITestCase):
    def setUp(self):
        # 유저 및 비즈니스 유저 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",  # 전화번호 추가
            gender="male",  # 성별 추가
            birth_date="1990-01-01",  # 생년월일 추가
        )
        self.host = BusinessUser.objects.create(user=self.user, business_number="123-45-67890")

        # 숙소 생성
        self.accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
            is_active=True,
        )

        # 방 생성
        self.room = Room.objects.create(
            accommodation=self.accommodation,
            name="Test Room",
            capacity=2,
            max_capacity=4,
            price=100.00,
            stay_type=True,
            description="Test Room Description",
            check_in_time="14:00:00",
            check_out_time="12:00:00",
        )

        # URL 설정
        self.url = reverse(
            "pages:booking_request", kwargs={"accommodation_pk": self.accommodation.pk, "pk": self.room.pk}
        )

    def test_booking_request_view_success(self):
        # 예약 요청을 위한 GET 요청
        response = self.client.get(
            self.url, {"check_in_date": "2024-11-01", "check_out_date": "2024-11-03", "guests_count": 2}
        )

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        data = response.json()
        self.assertIn("accommodation_name", data)
        self.assertIn("total_price", data)
        self.assertIn("check_in_date", data)
        self.assertIn("check_out_date", data)
        self.assertIn("guests_count", data)
        self.assertIn("room_info", data)

        # 특정 데이터 값 확인
        self.assertEqual(data["accommodation_name"], self.accommodation.name)
        self.assertEqual(data["room_info"]["name"], self.room.name)

    def test_booking_request_view_invalid_dates(self):
        # 잘못된 날짜 형식으로 요청
        response = self.client.get(
            self.url, {"check_in_date": "invalid-date", "check_out_date": "invalid-date", "guests_count": 2}
        )

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_request_view_no_guests_count(self):
        # 손님 수를 지정하지 않고 요청
        response = self.client.get(self.url, {"check_in_date": "2024-11-01", "check_out_date": "2024-11-03"})

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        data = response.json()
        self.assertEqual(data["guests_count"], 0)  # 기본값이 0인지 확인


# 부킹 상태 뷰 테스트 코드
class BookingStatusViewTest(APITestCase):

    def setUp(self):
        # 비즈니스 사용자 생성
        self.business_user = User.objects.create_user(
            email="business@example.com",
            password="password123",
            first_name="Business",
            last_name="Owner",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1980-01-01",
        )
        self.business_user_profile = BusinessUser.objects.create(
            user=self.business_user,
            business_number="123-45-67890",
            business_document=None,
            business_email="business@example.com",
            business_phonenumber="02-1234-5678",
            business_address="123 Business St, Business City",
        )

        # 일반 사용자 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
        )

        # 숙소 생성
        self.accommodation = Accommodation.objects.create(
            host=self.business_user_profile,  # BusinessUser 인스턴스를 할당
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
            is_active=True,
        )

        # 방 생성
        self.room = Room.objects.create(
            accommodation=self.accommodation,
            name="Test Room",
            capacity=2,
            max_capacity=4,
            price=100.00,
            stay_type=True,
            description="Test Room Description",
            check_in_time="14:00:00",
            check_out_time="12:00:00",
        )

        # 예약 생성
        self.booking = Booking.objects.create(
            guest=self.user,
            room=self.room,
            check_in_datetime="2024-12-01T14:00:00Z",
            check_out_datetime="2024-12-03T12:00:00Z",
            total_price=self.room.price,
            status="confirmed",
            booker_name="John Doe",
            booker_phone_number="010-1234-5678",
        )

        # URL 설정
        self.url = reverse("pages:booking_status", kwargs={"pk": self.booking.id})

        # APIClient 생성
        self.client = APIClient()

        # 사용자 로그인
        # 로그인 시도
        self.client.login(email="test@example.com", password="password123")


def test_booking_status_view_authenticated_user(self):
    # 로그인
    login_response = self.client.login(email="test@example.com", password="password123")
    self.assertTrue(login_response, "Login failed")  # 로그인 성공 여부 확인

    # 예약 상태 확인 요청
    response = self.client.get(self.url)

    # 응답 상태 코드 확인
    print("Response status code:", response.status_code)  # 상태 코드 출력
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 응답 데이터 확인
    data = response.json()
    self.assertEqual(data["id"], self.booking.id)
    self.assertEqual(data["booker_name"], "John Doe")
    self.assertEqual(data["total_price"], "100.00")  # 가격 형식 확인
    self.assertEqual(data["status"], "confirmed")


def test_booking_status_view_unauthenticated_user(self):
    # 로그아웃 상태에서 요청
    self.client.logout()
    response = self.client.get(self.url)

    # 응답 상태 코드 확인
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
