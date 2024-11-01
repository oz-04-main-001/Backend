# apps/rooms/tests/test_integration.py
import json

from django.urls import reverse
from rest_framework import status

from apps.rooms.tests.rooms_base import TestBase


class RoomIntegrationTest(TestBase):
    def setUp(self):
        super().setUp()
        self.create_url = reverse("rooms:room-list-create")
        self.user.user_type = "host"
        self.user.save()

        # 인증 설정
        self.client.force_authenticate(user=self.user)

    def test_complete_room_lifecycle(self):
        """방 생성부터 삭제까지의 전체 생명주기 테스트"""
        # 1. 방 생성 (첫 번째이자 유일한 요청)
        room_data = {
            **self.room_data,
            "accommodation": self.accommodation.id,
        }

        data = {
            "room": json.dumps(room_data),
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

        # 단일 POST 요청
        response = self.client.post(self.create_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. 생성된 방의 ID 추출
        room_id = response.data["room"]["id"]

        # 3. 방 정보 업데이트
        detail_url = reverse("rooms:room-detail", kwargs={"pk": room_id})
        update_data = {"name": "Updated Room", "price": 150000}
        response = self.client.patch(detail_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Room")

        # 4. 방 삭제
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_option_management(self):
        """옵션 관리 통합 테스트"""
        # 1. 기본 방 생성
        room_data = {
            **self.room_data,
            "accommodation": self.accommodation.id,
        }

        data = {
            "room": json.dumps(room_data),
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
        room_id = response.data["room"]["id"]

        # 2. 옵션 조회
        option_url = reverse("rooms:room-option", kwargs={"room_id": room_id})
        response = self.client.get(option_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. 옵션 선택지 조회
        choices_url = reverse("rooms:option-choices")
        response = self.client.get(choices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. 옵션 수정
        update_data = {
            "options": [{"name": "새로운 옵션", "category": "extra", "is_custom": True}, self.view_option.id]
        }
        response = self.client.put(option_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5. 특정 옵션 삭제
        option_ids = [self.view_option.id]
        delete_url = f"{option_url}?option_ids={','.join(map(str, option_ids))}"
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_error_scenarios(self):
        """에러 상황 통합 테스트"""
        # 1. 잘못된 방 생성 시도 (필수 데이터 누락)
        room_data = {
            **self.room_data,
            "accommodation": self.accommodation.id,
        }

        data = {
            "room": json.dumps({}),
            "room_type": json.dumps({"type_name": "standard"}),
            "inventory": json.dumps({"count_room": 0}),
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. 잘못된 옵션 데이터로 수정 시도
        room_data = data = {
            "room": json.dumps(room_data),
            "room_type": json.dumps({"type_name": "standard"}),
            "inventory": json.dumps({"count_room": 0}),
            "bed_options": json.dumps([{"bed_type": "single", "quantity": 2}]),
            "options": json.dumps(
                {
                    "new": [{"name": "특별 서비스", "category": "테스트용", "is_custom": True}],
                    "default": [{"option_id": self.view_option.id}],
                }
            ),
        }

        data["images"] = self.test_images

        response = self.client.post(self.create_url, room_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
