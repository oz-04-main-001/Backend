from django.urls import reverse
from rest_framework import status

from apps.rooms.models import Room, RoomInventory
from apps.rooms.tests.rooms_base import TestBase  # 같은 패키지 내의 base.py에서 import


class RoomViewTest(TestBase):
    def setUp(self):
        super().setUp()

        # API 테스트용 데이터 (ID 사용)
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

        # 모델 직접 생성용 데이터 (인스턴스 사용)
        self.room_data_for_model = {
            "accommodation": self.accommodation,  # 인스턴스 사용
            "name": "Test Room",
            "capacity": 2,
            "max_capacity": 4,
            "price": 100000,
            "stay_type": True,
            "check_in_time": "2024-10-21T14:00:00Z",
            "check_out_time": "2024-10-22T11:00:00Z",
            "is_available": True,
        }

    def test_create_room(self):
        url = reverse("rooms:room-list-create")
        response = self.client.post(url, self.room_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 1)

    def test_get_room_list(self):
        # 테스트용 방 생성 - 모델용 데이터 사용
        Room.objects.create(**self.room_data_for_model)

        url = reverse("rooms:room-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_get_room_detail(self):
        room = Room.objects.create(**self.room_data_for_model)
        url = reverse("rooms:room-detail", kwargs={"pk": room.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.room_data["name"])

    def test_update_room(self):
        room = Room.objects.create(**self.room_data_for_model)
        url = reverse("rooms:room-detail", kwargs={"pk": room.pk})

        # 필수 필드들인 'capacity'와 'max_capacity'를 함께 포함
        update_data = {
            "name": self.room_data_for_model["name"],
            "price": 150000,
            "capacity": self.room_data["capacity"],
            "max_capacity": self.room_data["max_capacity"],
        }

        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["price"], 150000)

    def test_delete_room(self):
        room = Room.objects.create(**self.room_data_for_model)
        RoomInventory.objects.create(room=room, count_room=10)  # RoomInventory 생성
        url = reverse("rooms:room-detail", kwargs={"pk": room.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Room.objects.count(), 0)

    def test_create_room_invalid_data(self):
        invalid_data = self.room_data.copy()  # API 테스트용 데이터 사용
        invalid_data["capacity"] = 5
        url = reverse("rooms:room-list-create")
        response = self.client.post(url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
