# apps/rooms/tests/test_models.py
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.rooms.models import Room, RoomType
from apps.rooms.tests.rooms_base import TestBase


class RoomModelTest(TestBase):
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

    def test_create_room(self):
        url = reverse("rooms:room-list-create")

        response = self.client.post(url, data=self.room_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 생성된 방 확인
        if response.status_code == status.HTTP_201_CREATED:
            room = Room.objects.get(id=response.data["id"])
            self.assertEqual(room.name, self.room_data["name"])
