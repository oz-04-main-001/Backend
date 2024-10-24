from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accommodations.models import Accommodation
from apps.users.models import BusinessUser, User


class BookingCheckViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email="test123@test.com", password="test123")
        self.host = BusinessUser.objects.create(
            user=self.user,
            business_email="test123@test.com",
            business_phonenumber="010-1234-1234",
            verification_status="pending",
        )
        self.accommodation = Accommodation.objects.create(host=self.host, name="test accommodation")

        # JWT 토큰 생성 및 클라이언트에 인증 헤더 생성
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

    def test_booking_check(self):
        # given
        url = reverse("host_management:host-management-booking-check")

        # when
        response = self.client.get(url)

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BookingRequestCheckViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email="test123@test.com", password="<PASSWORD>")
        self.host = BusinessUser.objects.create(
            user=self.user,
        )

    def test_booking_request_check(self):
        # given
        url = reverse("host_management:host-management-request-check")

        # when

        # then
