# apps/rooms/tests/test_serializers.py
from rest_framework.exceptions import ValidationError

from apps.rooms.models import Room
from apps.rooms.serializers.room_serializer import RoomSerializer
from apps.rooms.tests.rooms_base import TestBase


class RoomSerializerTest(TestBase):
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

    def test_valid_room_serializer(self):
        serializer = RoomSerializer(data=self.room_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_capacity(self):
        self.room_data["capacity"] = 5  # max_capacity보다 큰 값
        serializer = RoomSerializer(data=self.room_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("capacity", serializer.errors)

    def test_invalid_time_format(self):
        self.room_data["check_in_time"] = "invalid time"
        serializer = RoomSerializer(data=self.room_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("check_in_time", serializer.errors)

    def test_price_validation(self):
        self.room_data["price"] = -1000
        serializer = RoomSerializer(data=self.room_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_time_validation(self):  # test_check_in_out_time_validation에서 이렇게 변경
        self.room_data["check_out_time"] = self.room_data["check_in_time"]
        serializer = RoomSerializer(data=self.room_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("check_in_time", serializer.errors)
