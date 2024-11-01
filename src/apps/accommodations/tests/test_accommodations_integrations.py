import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.accommodations.models import Accommodation, Accommodation_Image
from apps.amenities.models import Amenity
from apps.users.models import BusinessUser

User = get_user_model()


class IntegrationTests(APITestCase):
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

    def tearDown(self):
        if self.host.business_document:
            self.host.business_document.delete()

    def create_test_image(self, filename="test.png"):
        """실제 이미지 데이터로 테스트 이미지 생성"""
        # 1x1 픽셀의 투명한 PNG 이미지 데이터
        small_gif = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return SimpleUploadedFile(filename, small_gif, content_type="image/png")

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

    def test_complete_accommodation_flow(self):
        """전체 숙소 관리 플로우 테스트"""
        # 1. 숙소 생성
        data = {
            "accommodation": json.dumps(self.accommodation_data),
            "accommodation_type": json.dumps(self.accommodation_type_data),
            "GPS_info": json.dumps(self.gps_info_data),
            "amenities": json.dumps(self.amenities_data),
            "images": self.test_image,  # files 대신 data에 직접 포함
        }

        create_url = reverse("accommodations:accommodation-list-create")  # URL 패턴 사용
        response = self.client.post(create_url, data=data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 중첩된 구조에서 ID 가져오기
        accommodation_id = response.data["accommodation"]["id"]
        # 2. 추가 이미지 업로드

        image_url = reverse("accommodations:accommodation-image-detail", kwargs={"pk": accommodation_id})
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        additional_image = SimpleUploadedFile(name="additional.gif", content=small_gif, content_type="image/gif")

        response = self.client.post(
            image_url,  # 이제 올바른 URL 형식인 '/api/v1/images/{id}/'로 요청됨
            {"images": additional_image},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. GPS 정보 업데이트
        accommodation_id = self.create_test_accommodation()
        new_gps_data = {
            "city": "Busan",
            "states": "Busan",
            "road_name": "Marine Drive",
            "address": "456 Marine Drive",
            "location": {"type": "Point", "coordinates": [129.0403, 35.1028]},
        }
        response = self.client.patch(
            f"/api/v1/accommodations/{accommodation_id}/gps-info/",
            data=json.dumps(new_gps_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6. 숙소 정보 업데이트
        detail_url = reverse("accommodations:accommodation-detail", kwargs={"pk": accommodation_id})
        update_data = {"name": "Updated Accommodation", "description": "Updated description that is still long enough"}
        response = self.client.patch(detail_url, data=json.dumps(update_data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Accommodation")

        # 7. choices API 테스트
        amenity_choices_url = reverse("accommodations:amenity-choices")
        response = self.client.get(amenity_choices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        accommodation_choices_url = reverse("accommodations:accommodation-choices")
        response = self.client.get(accommodation_choices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 8. 숙소 삭제
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_image_validation(self):
        """이미지 유효성 검사 테스트"""
        # 1. 숙소 생성
        data = {
            "accommodation": json.dumps(self.accommodation_data),
            "accommodation_type": json.dumps(self.accommodation_type_data),
            "GPS_info": json.dumps(self.gps_info_data),
            "amenities": json.dumps(self.amenities_data),
            "images": self.test_image,  # files 대신 data에 직접 포함
        }

        create_url = reverse("accommodations:accommodation-list-create")  # URL 패턴 사용
        response = self.client.post(create_url, data=data, format="multipart")

        if response.status_code != status.HTTP_201_CREATED:
            print("Error response:", getattr(response, "data", str(response)))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 중첩된 구조에서 ID 가져오기
        accommodation_id = response.data["accommodation"]["id"]

        # 2. 잘못된 파일 형식 테스트
        image_url = reverse("accommodations:accommodation-image-detail", kwargs={"pk": accommodation_id})
        invalid_file = SimpleUploadedFile("test.txt", b"invalid image content", content_type="text/plain")

        response = self.client.post(
            image_url, {"images": [invalid_file], "delete_existing": "false"}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
