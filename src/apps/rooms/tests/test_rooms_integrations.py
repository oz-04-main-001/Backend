# apps/rooms/tests/test_integration.py
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from apps.rooms.tests.rooms_base import TestBase


class RoomIntegrationTest(TestBase):
    def setUp(self):
        super().setUp()
        self.room_data = {
            "accommodation": self.accommodation.id,
            "name": "Test Room",
            "capacity": 2,
            "max_capacity": 4,
            "price": 100000,
            "stay_type": True,
            "check_in_time": "2024-10-21T14:00:00Z",
            "check_out_time": "2024-10-22T11:00:00Z",
            "is_available": True,
        }

    def test_complete_room_lifecycle(self):
        """방 생성부터 삭제까지의 전체 생명주기 테스트"""
        # 1. 방 생성
        create_url = reverse("rooms:room-list-create")
        response = self.client.post(create_url, self.room_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        room_id = response.data["id"]

        # 2. 룸타입 추가
        room_type_data = {"room": room_id, "type_name": "standard", "is_customized": False}
        type_url = reverse("rooms:room-type-list-create")
        response = self.client.post(type_url, room_type_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. 이미지 추가 (실제 이미지가 필요해 추가 테스트는 보류)
        # image_data = SimpleUploadedFile(
        #     name='test_room.jpg',
        #     content=b'test_image_content',  # 간단한 테스트 데이터
        #     content_type='image/jpeg'
        # )
        # image_url = reverse('rooms:room-add-image', kwargs={'pk': room_id})
        # response = self.client.post(
        #     image_url,
        #     {'image': image_data},
        #     format='multipart'
        # )
        # print("Image Addition Response:", response.status_code, response.content)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 4. 방 정보 수정
        update_data = {
            "name": "Updated Room Name",
            "price": 150000,
            "capacity": self.room_data["capacity"],
            "max_capacity": self.room_data["max_capacity"],
        }
        detail_url = reverse("rooms:room-detail", kwargs={"pk": room_id})
        response = self.client.patch(detail_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["price"], 150000)

        # 5. 재고 확인
        inventory_url = reverse("rooms:room-inventory-list")
        response = self.client.get(f"{inventory_url}?room__accommodation={self.accommodation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["count_room"], 1)

        # 6. 방 삭제
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_room_type_integration(self):
        """룸타입 관련 통합 테스트"""
        # 1. 방 생성
        create_url = reverse("rooms:room-list-create")
        response = self.client.post(create_url, self.room_data, format="json")
        room_id = response.data["id"]

        # 2. 기본 룸타입 생성
        room_type_data = {"room": room_id, "type_name": "standard", "is_customized": False}
        type_url = reverse("rooms:room-type-list-create")
        response = self.client.post(type_url, room_type_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. 중복 룸타입 생성 시도 (실패해야 함)
        response = self.client.post(type_url, room_type_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_room_inventory_integration(self):
        """방 재고 관리 통합 테스트"""
        # 1. 방 생성
        create_url = reverse("rooms:room-list-create")
        response = self.client.post(create_url, self.room_data, format="json")
        room_id = response.data["id"]

        # 2. 재고 확인
        inventory_url = reverse("rooms:room-inventory-list")
        response = self.client.get(inventory_url)
        initial_inventory = response.data[0]["count_room"]
        self.assertEqual(initial_inventory, 1)

        # 3. 방 비활성화 (모든 필수 필드 포함)
        detail_url = reverse("rooms:room-detail", kwargs={"pk": room_id})
        update_data = {
            "is_available": False,
            "capacity": self.room_data["capacity"],
            "max_capacity": self.room_data["max_capacity"],
            "price": self.room_data["price"],
            "name": self.room_data["name"],
        }
        response = self.client.patch(detail_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_error_scenarios(self):
        """에러 상황 통합 테스트"""
        # 1. 잘못된 용량으로 방 생성
        invalid_room_data = self.room_data.copy()
        invalid_room_data["capacity"] = 5  # max_capacity보다 큼
        invalid_room_data["max_capacity"] = 3

        create_url = reverse("rooms:room-list-create")
        response = self.client.post(create_url, invalid_room_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. 존재하지 않는 방에 룸타입 추가
        room_type_data = {"room": 99999, "type_name": "Deluxe", "is_customized": True}
        type_url = reverse("rooms:room-type-list-create")
        response = self.client.post(type_url, room_type_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. 잘못된 형식의 이미지 업로드
        response = self.client.post(create_url, self.room_data, format="json")
        room_id = response.data["id"]

        invalid_image = SimpleUploadedFile(name="test.txt", content=b"invalid image content", content_type="text/plain")
        image_url = reverse("rooms:room-add-image", kwargs={"pk": room_id})
        response = self.client.post(image_url, {"image": invalid_image}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
