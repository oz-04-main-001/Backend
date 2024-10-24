# apps/core/test_base.py
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.accommodations.models import Accommodation, AccommodationType
from apps.users.models import BusinessUser

User = get_user_model()


class TestBase(APITestCase):
    def setUp(self):
        # 테스트 문서 파일 생성
        self.test_document = SimpleUploadedFile(
            name="business_doc.pdf", content=b"test document content", content_type="application/pdf"
        )

        # 사용자 및 비즈니스 사용자 생성
        self.user = User.objects.create_superuser(email="test@test.com", password="testpass123")
        self.host = BusinessUser.objects.create(
            user=self.user, business_document=self.test_document, business_number="123-45-67890"
        )

        # 숙소 데이터 설정
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

        # 먼저 숙소 생성 (accommodation_type 없이)
        self.accommodation = Accommodation.objects.create(
            name=self.accommodation_data["name"],
            host=self.host,
            phone_number=self.accommodation_data["phone_number"],
            description=self.accommodation_data["description"],
            rules=self.accommodation_data["rules"],
            # city=self.accommodation_data["gps_info"]["city"],
            # states=self.accommodation_data["gps_info"]["states"],
            # road_name=self.accommodation_data["gps_info"]["road_name"],
            # address=self.accommodation_data["gps_info"]["address"],
            # location=self.accommodation_data["gps_info"]["location"]
        )

        # 그 다음 숙소 타입 생성
        self.accommodation_type = AccommodationType.objects.create(
            type_name="Hotel", is_customized=False, accommodation=self.accommodation  # 이미 생성된 accommodation 참조
        )

        # 마지막으로 숙소에 타입 연결
        self.accommodation.accommodation_type = self.accommodation_type
        self.accommodation.save()

        self.client.force_authenticate(user=self.user)
