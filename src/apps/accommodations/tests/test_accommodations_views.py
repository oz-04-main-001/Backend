import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accommodations.models import Accommodation, GPS_Info
from apps.amenities.models import Amenity
from apps.users.models import BusinessUser

User = get_user_model()


class ViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email="test@test.com", password="testpass123")
        self.test_document = SimpleUploadedFile(
            name="test_document.pdf", content=b"test document content", content_type="application/pdf"
        )
        self.host = BusinessUser.objects.create(
            user=self.user, business_document=self.test_document, business_number="123-45-67890"
        )

        self.amenity = Amenity.objects.create(
            id=1, name="수영장", category="basic", is_custom=False  # 명시적으로 ID 1을 가진 Amenity 생성
        )

        # Create a small valid PNG image
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )

        self.test_image = SimpleUploadedFile(name="test.gif", content=small_gif, content_type="image/gif")

        # Base accommodation data
        self.accommodation_data = {
            "name": "Test Hotel",
            "description": "A nice hotel for testing that is long enough",
            "rules": "No smoking, no pets are allowed here",
        }

        self.accommodation_type_data = {"type_name": "호텔", "is_customized": False}

        self.gps_info_data = {
            "city": "Seoul",
            "states": "Seoul",
            "road_name": "Test Road",
            "address": "123 Test Road",
            "location": {"type": "Point", "coordinates": [127.0295, 37.4979]},
        }

        self.amenities_data = {"new": [], "default": [{"amenity_id": self.amenity.id, "custom_value": None}]}

    def create_test_accommodation(self):
        """테스트용 숙소 생성 헬퍼 메서드"""
        # Create a new instance of test image file for each request
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        test_image = SimpleUploadedFile(name="test.gif", content=small_gif, content_type="image/gif")

        data = {
            "accommodation": json.dumps(self.accommodation_data),
            "accommodation_type": json.dumps(self.accommodation_type_data),
            "GPS_info": json.dumps(self.gps_info_data),
            "amenities": json.dumps(self.amenities_data),
            "images": test_image,
        }
        response = self.client.post("/api/v1/accommodations/", data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        accommodation_id = None
        if "id" in response.data:
            accommodation_id = response.data["id"]
        elif "accommodation" in response.data and "id" in response.data["accommodation"]:
            accommodation_id = response.data["accommodation"]["id"]

        self.assertIsNotNone(accommodation_id, "생성된 숙소의 ID를 찾을 수 없습니다.")
        return accommodation_id

    def test_create_accommodation(self):
        """숙소 생성 API 테스트"""
        data = {
            "accommodation": json.dumps(self.accommodation_data),
            "accommodation_type": json.dumps(self.accommodation_type_data),
            "GPS_info": json.dumps(self.gps_info_data),
            "amenities": json.dumps(self.amenities_data),
            "images": self.test_image,  # files 대신 data에 직접 포함
        }

        response = self.client.post("/api/v1/accommodations/", data=data, format="multipart")  # format 지정

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_accommodation(self):
        """숙소 정보 수정 테스트"""
        accommodation_id = self.create_test_accommodation()

        update_data = {
            "name": "Updated Hotel Name",
            "description": "Updated description that is long enough for sure",
            "rules": "Updated rules that are very clear and detailed",
        }

        response = self.client.patch(
            f"/api/v1/accommodations/{accommodation_id}/", data=json.dumps(update_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], update_data["name"])

    def test_delete_accommodation(self):
        """숙소 삭제 테스트"""
        accommodation_id = self.create_test_accommodation()

        response = self.client.delete(f"/api/v1/accommodations/{accommodation_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_gps_info_update(self):
        """GPS 정보 업데이트 테스트"""
        accommodation_id = self.create_test_accommodation()

        gps_update_data = {
            "city": "Busan",
            "states": "Busan",
            "road_name": "Updated Road",
            "address": "456 Updated Road",
            "location": {"type": "Point", "coordinates": [129.0756, 35.1796]},
        }

        response = self.client.put(
            f"/api/v1/accommodations/{accommodation_id}/gps-info/",
            data=json.dumps(gps_update_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], gps_update_data["city"])

    def tearDown(self):
        if self.test_image:
            self.test_image.close()
        if self.host.business_document:
            self.host.business_document.delete()
