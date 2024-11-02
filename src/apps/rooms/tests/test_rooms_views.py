# apps/rooms/tests/test_views.py
import json

from django.urls import reverse
from rest_framework import status

from apps.amenities.models import Option, RoomOption
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.rooms.tests.rooms_base import TestBase


class RoomViewTest(TestBase):
    def setUp(self):
        super().setUp()
        self.create_url = reverse("rooms:room-list-create")
        self.user.user_type = "host"
        self.user.save()

        # 인증 설정
        self.client.force_authenticate(user=self.user)

    def test_create_room_with_complete_data(self):
        """전체 데이터로 Room 생성 테스트"""
        room_data = {
            "accommodation": self.accommodation.id,  # 이 부분 추가
            "name": "Test Room",
            "capacity": 2,
            "max_capacity": 1000,
            "price": 100000,
            "stay_type": True,
            "description": "Test Room Description",
            "check_in_time": "15:00:00",
            "check_out_time": "11:00:00",
            "is_available": True,
        }

        data = {
            "room": json.dumps(room_data),  # 수정된 room_data 사용
            "room_type": json.dumps({"type_name": "standard"}),
            "inventory": json.dumps({"count_room": 5}),
            "bed_options": json.dumps([{"bed_type": "single", "quantity": 2}]),
            "options": json.dumps(
                {
                    "new": [{"name": "특별 서비스", "category": "extra", "is_custom": True}],
                    "default": [{"option_id": self.view_option.id}],
                }
            ),
        }

        data["images"] = self.test_images

        response = self.client.post(self.create_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("room", response.data)
        self.assertIn("room_type", response.data)
        self.assertIn("inventory", response.data)
        self.assertIn("options", response.data)
        self.assertIn("bed_options", response.data)

    def test_get_room_detail(self):
        """Room 상세 조회 테스트"""
        url = reverse("rooms:room-detail", kwargs={"pk": self.room.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.room.name)

    def test_update_room(self):
        """Room 수정 테스트"""
        url = reverse("rooms:room-detail", kwargs={"pk": self.room.pk})
        update_data = {"name": "Updated Room Name", "price": 200000}
        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Room Name")

    def test_delete_room(self):
        """Room 삭제 테스트"""
        url = reverse("rooms:room-detail", kwargs={"pk": self.room.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Room.objects.filter(id=self.room.pk).count(), 0)


class RoomOptionViewTest(TestBase):
    def setUp(self):
        super().setUp()
        self.option_url = reverse("rooms:room-option", kwargs={"room_id": self.room.id})
        self.user.user_type = "host"
        self.user.save()

        # 인증 설정
        self.client.force_authenticate(user=self.user)

    def test_get_room_options(self):
        """Room 옵션 조회 테스트"""
        response = self.client.get(self.option_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_room_options(self):
        """Room 옵션 수정 테스트"""
        data = {"options": [{"name": "새로운 옵션", "category": "extra", "is_custom": True}, self.bathroom_option.id]}
        response = self.client.put(self.option_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_room_options(self):
        """Room 옵션 삭제 테스트"""
        # 특정 옵션만 삭제
        option_ids = [self.bathroom_option.id]
        url = f"{self.option_url}?option_ids={','.join(map(str, option_ids))}"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 옵션이 실제로 삭제되었는지 확인
        self.assertFalse(RoomOption.objects.filter(room=self.room, option_id__in=option_ids).exists())

    def test_delete_all_room_options(self):
        """Room의 모든 옵션 삭제 테스트"""
        response = self.client.delete(self.option_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RoomOption.objects.filter(room=self.room).count(), 0)
