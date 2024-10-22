from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accommodations.serializers.accommodation_serializer import (
    AccommodationSerializer,
)
from apps.users.models import BusinessUser

User = get_user_model()


class SerializerTests(TestCase):
    """단위 테스트: 시리얼라이저"""

    def setUp(self):
        self.client = APIClient()
        self.test_document = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"test document content",  # 바이너리 형태의 컨텐츠
            content_type="application/pdf",
        )
        self.user = User.objects.create_superuser(email="test@test.com", password="testpass123")
        self.host = BusinessUser.objects.create(
            user=self.user, business_document=self.test_document, business_number="123-45-67890"
        )
        self.accommodation_data = {
            "name": "Test Accommodation",
            "phone_number": "02-1234-5678",
            "description": "Test Description that is long enough",
            "rules": "Test Rules that are clear",
            "accommodation_type": {"type_name": "Hotel", "is_customized": False},
            "gps_info": {
                "city": "Seoul",
                "states": "Seoul",
                "road_name": "Gangnam-daero",
                "address": "123 Gangnam-daero",
                "location": {"type": "Point", "coordinates": [127.0295, 37.4979]},
            },
        }

    def tearDown(self):
        # 테스트 후 파일 정리
        if self.host.business_document:
            self.host.business_document.delete()

    def test_valid_accommodation_serializer(self):
        """유효한 데이터 검증"""
        serializer = AccommodationSerializer(data=self.accommodation_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_phone_number(self):
        """전화번호 유효성 검사"""
        self.accommodation_data["phone_number"] = "invalid-phone"
        serializer = AccommodationSerializer(data=self.accommodation_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_invalid_description(self):
        """설명 길이 유효성 검사"""
        self.accommodation_data["description"] = "too short"
        serializer = AccommodationSerializer(data=self.accommodation_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)
