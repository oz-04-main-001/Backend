from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accommodations.models import Accommodation
from apps.accommodations.serializers.accommodation_serializer import (
    AccommodationSerializer,
    GPSInfoSerializer,
)
from apps.amenities.models import Amenity
from apps.amenities.serializers.amenities_serializers import (
    AccommodationAmenitySerializer,
    AmenitySerializer,
)
from apps.users.models import BusinessUser

User = get_user_model()


class SerializerTests(TestCase):
    """단위 테스트: 시리얼라이저"""

    def setUp(self):
        self.client = APIClient()
        self.test_document = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"test document content",
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
        self.amenity = Amenity.objects.create(name="수영장", category="basic")

    def tearDown(self):
        if self.host.business_document:
            self.host.business_document.delete()

    def test_valid_amenity_serializer(self):
        """새로운 어메니티 생성 테스트"""
        serializer = AmenitySerializer(
            data={
                "name": "수영장",  # AMENITY_CHOICES에 있는 유효한 값으로 변경
                "category": "basic",
                "is_custom": False,
            }
        )
        self.assertTrue(serializer.is_valid())

    def test_invalid_accommodation_amenity(self):
        """잘못된 숙소-어메니티 연결 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            description="Test Description that is long enough",
            rules="Test Rules that are clear",
        )

        # 존재하지 않는 어메니티 ID
        data = {"amenity_id": 999, "custom_value": None}

        serializer = AccommodationAmenitySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("amenity_id", serializer.errors)  # 'amenity'를 'amenity_id'로 수정

    def test_accommodation_amenity_serializer(self):
        """숙소-어메니티 연결 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            description="Test Description that is long enough",
            rules="Test Rules that are clear",
        )

        data = {"amenity_id": self.amenity.id, "custom_value": None}

        serializer = AccommodationAmenitySerializer(data=data)
        self.assertTrue(serializer.is_valid())

        instance = serializer.save(accommodation=accommodation)
        self.assertEqual(instance.amenity, self.amenity)
