from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
)
from apps.users.models import BusinessUser

User = get_user_model()


class ModelTests(TestCase):
    """단위 테스트: 모델"""

    def setUp(self):
        # 테스트 유저 및 호스트 생성
        self.test_document = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"test document content",  # 바이너리 형태의 컨텐츠
            content_type="application/pdf",
        )
        self.user = User.objects.create_superuser(email="test@test.com", password="testpass123")
        self.host = BusinessUser.objects.create(
            user=self.user, business_document=self.test_document, business_number="123-45-67890"
        )

    def tearDown(self):
        # 테스트 후 파일 정리
        if self.host.business_document:
            self.host.business_document.delete()

    def test_business_document_upload(self):
        self.assertTrue(self.host.business_document)
        self.assertIn("test_document.pdf", self.host.business_document.name)

    def test_accommodation_creation(self):
        """숙소 생성 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )
        self.assertEqual(accommodation.name, "Test Accommodation")
        self.assertEqual(accommodation.host, self.host)
        self.assertTrue(accommodation.is_active)
        self.assertIsNone(accommodation.average_rating)

    def test_accommodation_update(self):
        """숙소 정보 수정 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )

        # 정보 수정
        accommodation.name = "Updated Name"
        accommodation.phone_number = "02-9876-5432"
        accommodation.save()

        # DB에서 다시 조회
        updated_accommodation = Accommodation.objects.get(id=accommodation.id)
        self.assertEqual(updated_accommodation.name, "Updated Name")
        self.assertEqual(updated_accommodation.phone_number, "02-9876-5432")

    def test_accommodation_type_creation(self):
        """숙소 타입 생성 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )
        acc_type = AccommodationType.objects.create(accommodation=accommodation, type_name="Hotel", is_customized=False)
        self.assertEqual(acc_type.type_name, "Hotel")
        self.assertFalse(acc_type.is_customized)
        self.assertEqual(acc_type.accommodation, accommodation)

    def test_accommodation_type_update(self):
        """숙소 타입 수정 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )
        acc_type = AccommodationType.objects.create(accommodation=accommodation, type_name="Hotel", is_customized=False)

        # 타입 정보 수정
        acc_type.type_name = "Resort"
        acc_type.is_customized = True
        acc_type.save()

        # DB에서 다시 조회
        updated_type = AccommodationType.objects.get(id=acc_type.id)
        self.assertEqual(updated_type.type_name, "Resort")
        self.assertTrue(updated_type.is_customized)

    def test_gps_info_creation(self):
        """GPS 정보 생성 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )
        gps_info = GPS_Info.objects.create(
            accommodation=accommodation,
            city="Seoul",
            states="Seoul",
            road_name="Gangnam-daero",
            address="123 Gangnam-daero",
            location=Point(127.0295, 37.4979),
        )
        self.assertEqual(gps_info.city, "Seoul")
        self.assertEqual(gps_info.location.coords, (127.0295, 37.4979))
        self.assertEqual(gps_info.accommodation, accommodation)

    def test_gps_info_update(self):
        """GPS 정보 수정 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )
        gps_info = GPS_Info.objects.create(
            accommodation=accommodation,
            city="Seoul",
            states="Seoul",
            road_name="Gangnam-daero",
            address="123 Gangnam-daero",
            location=Point(127.0295, 37.4979),
        )

        # GPS 정보 수정
        gps_info.city = "Busan"
        gps_info.location = Point(129.0403, 35.1028)
        gps_info.save()

        # DB에서 다시 조회
        updated_gps = GPS_Info.objects.get(id=gps_info.id)
        self.assertEqual(updated_gps.city, "Busan")
        self.assertEqual(updated_gps.location.coords, (129.0403, 35.1028))

    def test_accommodation_deletion(self):
        """숙소 삭제 시 연관 데이터 삭제 테스트"""
        # 숙소 및 연관 데이터 생성
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )

        acc_type = AccommodationType.objects.create(accommodation=accommodation, type_name="Hotel", is_customized=False)

        gps_info = GPS_Info.objects.create(
            accommodation=accommodation,
            city="Seoul",
            states="Seoul",
            road_name="Gangnam-daero",
            address="123 Gangnam-daero",
            location=Point(127.0295, 37.4979),
        )

        # 숙소 삭제
        accommodation.delete()

        # 연관 데이터도 삭제되었는지 확인
        self.assertEqual(AccommodationType.objects.filter(id=acc_type.id).count(), 0)
        self.assertEqual(GPS_Info.objects.filter(id=gps_info.id).count(), 0)

    def test_unique_accommodation_type(self):
        """숙소당 하나의 타입만 가질 수 있는지 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )

        AccommodationType.objects.create(accommodation=accommodation, type_name="Hotel", is_customized=False)

        # 같은 숙소에 대해 두 번째 타입 생성 시도
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AccommodationType.objects.create(accommodation=accommodation, type_name="Resort", is_customized=True)

    def test_unique_gps_info(self):
        """숙소당 하나의 GPS 정보만 가질 수 있는지 테스트"""
        accommodation = Accommodation.objects.create(
            host=self.host,
            name="Test Accommodation",
            phone_number="02-1234-5678",
            description="Test Description",
            rules="Test Rules",
        )

        GPS_Info.objects.create(
            accommodation=accommodation,
            city="Seoul",
            states="Seoul",
            road_name="Gangnam-daero",
            address="123 Gangnam-daero",
            location=Point(127.0295, 37.4979),
        )

        # 같은 숙소에 대해 두 번째 GPS 정보 생성 시도
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GPS_Info.objects.create(
                    accommodation=accommodation,
                    city="Busan",
                    states="Busan",
                    road_name="Marine Drive",
                    address="456 Marine Drive",
                    location=Point(129.0403, 35.1028),
                )
