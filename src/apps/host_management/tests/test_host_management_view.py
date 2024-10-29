from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.accommodations.models import Accommodation
from apps.bookings.models import Booking
from apps.rooms.models import Room
from apps.users.models import BusinessUser


class BookingAPITestCase(APITestCase):
    def setUp(self):
        # Given: 테스트용 데이터 설정
        self.api_client = APIClient()

        # 일반 사용자 생성
        self.user = get_user_model().objects.create_user(
            email="testuser@naver.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone_number="010-1234-5678",
            gender="M",
            birth_date="1997-01-01",
        )

        # 비즈니스 사용자 생성
        self.business_user_account = get_user_model().objects.create_user(
            email="businessuser@naver.com",
            password="testpass1234",
            first_name="Business",
            last_name="Owner",
            phone_number="010-8765-4321",
            gender="M",
            birth_date="1980-01-01",
            is_staff=True,
        )

        # BusinessUser 인스턴스 생성
        self.business_user = BusinessUser.objects.create(
            user=self.business_user_account,
            business_number="1234567890",
            business_email=self.business_user_account.email,
            business_phonenumber=self.business_user_account.phone_number,
        )

        # 숙소 생성
        self.accommodation = Accommodation.objects.create(
            name="Test Accommodation", phone_number="010-1111-2222", host=self.business_user
        )

        # 방 생성
        self.room = Room.objects.create(
            accommodation=self.accommodation,
            name="Room 101",
            capacity=2,
            max_capacity=4,
            price=150000,
            stay_type=True,
            check_in_time="14:00",
            check_out_time="11:00",
        )

        # 예약 생성 (시간대 포함)
        self.booking = Booking.objects.create(
            guest=self.user,
            room=self.room,
            check_in_datetime=timezone.make_aware(datetime(2024, 11, 1, 14, 0)),
            check_out_datetime=timezone.make_aware(datetime(2024, 11, 5, 11, 0)),
            status="pending",
            booker_name=self.user.first_name,
            booker_phone_number=self.user.phone_number,
            total_price=600000,
        )

    # 예약 목록 뷰 테스트 (전체 목록 확인)
    def test_booking_list_view(self):
        # given
        pass
        # when

        # then
