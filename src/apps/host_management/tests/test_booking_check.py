from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from apps.bookings.models import Booking
from datetime import date

class BookingListViewTest(APITestCase):
    def setUp(self):
        # Given: 테스트용 유저 및 예약 데이터 생성
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.booking = Booking.objects.create(
            guest=self.user,
            room_id=1,
            check_in_date=date(2024, 10, 20),
            check_out_date=date(2024, 10, 22),
            status="pending"
        )

    def test_get_booking_list_valid_date_and_room(self):
        # Given: 유효한 날짜와 room_id가 주어졌을 때
        selected_date = "2024-10-20"
        room_id = 1
        url = f"/bookings/?date={selected_date}&room_id={room_id}"

        # When: GET 요청을 보낼 때
        response = self.client.get(url)

        # Then: 예약 목록이 반환되고 상태 코드가 200이어야 함
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "pending")

    def test_get_booking_list_missing_date(self):
        # Given: 날짜가 없을 때
        room_id = 1
        url = f"/bookings/?room_id={room_id}"

        # When: GET 요청을 보낼 때
        response = self.client.get(url)

        # Then: 오류 메시지가 반환되고 상태 코드가 400이어야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "날짜를 선택 해 주세요.")

class BookingRequestCheckViewTest(APITestCase):
    def setUp(self):
        # Given: 테스트용 유저 및 예약 데이터 생성
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.booking = Booking.objects.create(
            guest=self.user,
            room_id=1,
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

    def test_patch_booking_invalid_action(self):
        # Given: 예약이 존재하고 잘못된 action 요청이 주어졌을 때
        url = f"/bookings/{self.booking.id}/action/"
        data = {"action": "invalid"}

        # When: PATCH 요청을 보낼 때
        response = self.client.patch(url, data)

        # Then: 오류 메시지가 반환되고 상태 코드가 400이어야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid action")
