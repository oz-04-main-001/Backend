import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.accommodations.models import Accommodation
from apps.users.models import BusinessUser

User = get_user_model()


class IntegrationTests(APITestCase):
    """통합 테스트: 전체 플로우"""

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

    def test_complete_accommodation_flow(self):
        """전체 숙소 관리 플로우 테스트"""
        # 1. 숙소 생성
        create_url = reverse("accommodations:accommodation-list-create")
        response = self.client.post(
            create_url, data=json.dumps(self.accommodation_data), content_type="application/json"
        )
        assert response.status_code == status.HTTP_201_CREATED, f"Failed to create accommodation: {response.data}"
        self.test_accommodation = Accommodation.objects.get(name="Test Accommodation")
        if response.status_code != status.HTTP_201_CREATED:
            print("Creation Error:", response.data)  # 에러 내용 출력
            raise ValueError("Failed to create test accommodation")
        accommodation_id = response.data["id"]

        # 2. 숙소 정보 조회
        detail_url = reverse("accommodations:accommodation-detail", kwargs={"pk": accommodation_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Accommodation")

        # 3. 숙소 정보 업데이트
        update_data = {"name": "Updated Accommodation", "description": "Updated description that is still long enough"}
        response = self.client.patch(detail_url, data=json.dumps(update_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Accommodation")

        # 4. GPS 정보 업데이트
        gps_url = reverse("accommodations:gps-info-detail", kwargs={"accommodation_id": accommodation_id})
        new_gps_data = {
            "city": "Busan",
            "states": "Busan",
            "road_name": "Marine Drive",
            "address": "456 Marine Drive",
            "location": {"type": "Point", "coordinates": [129.0403, 35.1028]},
        }
        response = self.client.patch(gps_url, data=json.dumps(new_gps_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5. 숙소 삭제
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 6. 삭제 확인
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
