from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accommodations.models import Accommodation
from apps.bookings.models import Booking
from apps.rooms.models import Room
from apps.users.models import User


class BookingListViewTest(APITestCase):
    def setUp(self):
        # Given: 테스트용 유저, 숙소 및 예약 데이터 생성
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.accommodation = Accommodation.objects.create(
            host=self.user,
            name="Test Accommodation",
            description="Test Description",
            price_per_night=100.00,
            is_active=True
        )
        self.room = Room.objects.create(
            name="Room 101",
            capacity=2,
            max_capacity=4,
            price=150,
            stay_type=True,
            description="A cozy room",
            check_in_time="14:00:00",
            check_out_time="11:00:00",
            is_available=True,
            accommodation=self.accommodation
        )
        self.booking = Booking.objects.create(
            guest=self.user,
            room=self.room,
            accommodation=self.accommodation,
            check_in_date=date(2024, 10, 20),
            check_out_date=date(2024, 10, 22),
            status="pending"
        )

    def test_get_booking_list_valid_date_in_range(self):
        # Given: 유효한 날짜와 room_id, host_id가 주어졌을 때 (날짜가 예약 기간 내에 있음)
        selected_date = "2024-10-21"
        room_id = self.room.id
        host_id = self.user.id
        url = f"/bookings/?date={selected_date}&room_id={room_id}&host_id={host_id}"

        # When: GET 요청을 보낼 때
        response = self.client.get(url)

        # Then: 예약 목록이 반환되고 상태 코드가 200이어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "pending")

    def test_get_booking_list_date_out_of_range(self):
        # Given: 유효한 날짜와 room_id, host_id가 주어졌을 때 (날짜가 예약 기간에 포함되지 않음)
        selected_date = "2024-10-25"
        room_id = self.room.id
        host_id = self.user.id
        url = f"/bookings/?date={selected_date}&room_id={room_id}&host_id={host_id}"

        # When: GET 요청을 보낼 때
        response = self.client.get(url)

        # Then: 빈 예약 목록이 반환되고 상태 코드가 200이어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_booking_list_missing_date(self):
        # Given: 날짜가 없고 room_id와 host_id만 주어졌을 때
        room_id = self.room.id
        host_id = self.user.id
        url = f"/bookings/?room_id={room_id}&host_id={host_id}"

        # When: GET 요청을 보낼 때
        response = self.client.get(url)

        # Then: 오류 메시지가 반환되고 상태 코드가 400이어야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "날짜를 선택 해 주세요.")

    def test_get_booking_list_invalid_date_format(self):
        # Given: 유효하지 않은 날짜 형식이 주어졌을 때
        selected_date = "invalid-date"
        room_id = self.room.id
        host_id = self.user.id
        url = f"/bookings/?date={selected_date}&room_id={room_id}&host_id={host_id}"

        # When: GET 요청을 보낼 때
        response = self.client.get(url)

        # Then: 오류 메시지가 반환되고 상태 코드가 400이어야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BookingRequestCheckViewTest(APITestCase):
    def setUp(self):
        # Given: 테스트용 유저 및 예약 데이터 생성
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.accommodation = Accommodation.objects.create(
            host=self.user,
            name="Test Accommodation",
            description="Test Description",
            price_per_night=100.00,
            is_active=True
        )
        self.room = Room.objects.create(
            name="Room 101",
            capacity=2,
            max_capacity=4,
            price=150,
            stay_type=True,
            description="A cozy room",
            check_in_time="14:00:00",
            check_out_time="11:00:00",
            is_available=True,
            accommodation=self.accommodation
        )
        self.booking = Booking.objects.create(
            guest=self.user,
            room=self.room,
            accommodation=self.accommodation,
            check_in_date=date(2024, 10, 20),
            check_out_date=date(2024, 10, 22),
            status="pending"
        )

    def test_patch_booking_accept(self):
        # Given: 예약이 존재하고 수락 요청이 주어졌을 때
        url = f"/bookings/{self.booking.id}/action/"
        data = {"action": "accept"}

        # When: PATCH 요청을 보낼 때
        response = self.client.patch(url, data)

        # Then: 예약 상태가 "confirmed"로 변경되고 상태 코드가 200이어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "confirmed")
        # 추가: 예약 수락 이후 알림 확인 로직 추가 가능

    def test_patch_booking_reject(self):
        # Given: 예약이 존재하고 거절 요청이 주어졌을 때
        url = f"/bookings/{self.booking.id}/action/"
        data = {"action": "reject"}

        # When: PATCH 요청을 보낼 때
        response = self.client.patch(url, data)

        # Then: 예약 상태가 "rejected"로 변경되고 상태 코드가 200이어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "rejected")
        # 추가: 예약 거절 이후 후속 작업(예: 취소 알림) 확인 로직 추가 가능

    def test_patch_booking_use_complete(self):
        # Given: 예약이 존재하고 사용 완료 요청이 주어졌을 때
        url = f"/bookings/{self.booking.id}/action/"
        data = {"action": "Use complete"}

        # When: PATCH 요청을 보낼 때
        response = self.client.patch(url, data)

        # Then: 예약 상태가 "Use complete"로 변경되고 상태 코드가 200이어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Use complete")

    def test_patch_booking_invalid_action(self):
        # Given: 예약이 존재하고 잘못된 action 요청이 주어졌을 때
        url = f"/bookings/{self.booking.id}/action/"
        data = {"action": "invalid"}

        # When: PATCH 요청을 보낼 때
        response = self.client.patch(url, data)

        # Then: 오류 메시지가 반환되고 상태 코드가 400이어야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid action")

    def test_patch_booking_canceled(self):
        # Given: 예약이 존재하고 취소 요청이 주어졌을 때
        url = f"/bookings/{self.booking.id}/action/"
        data = {"action": "canceled"}

        # When: PATCH 요청을 보낼 때
        response = self.client.patch(url, data)

        # Then: 예약 상태가 "canceled"로 변경되고 상태 코드가 200이어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "canceled")