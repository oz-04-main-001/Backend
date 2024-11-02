# apps/rooms/tests/test_serializers.py
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from apps.amenities.serializers.amenities_serializers import OptionSerializer
from apps.rooms.serializers.room_serializer import (
    BedOptionSerializer,
    RoomImageSerializer,
    RoomInventorySerializer,
    RoomSerializer,
    RoomTypeSerializer,
)
from apps.rooms.tests.rooms_base import TestBase


class RoomSerializerTest(TestBase):
    def test_valid_room_serializer(self):
        """유효한 데이터로 Room 생성"""
        serializer = RoomSerializer(data={"accommodation": self.accommodation.id, **self.room_data})
        self.assertTrue(serializer.is_valid())

    def test_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        data = {}  # 아무 필드도 없는 데이터
        serializer = RoomSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


class RoomTypeSerializerTest(TestBase):
    def test_valid_room_type(self):
        """유효한 방 타입 생성"""
        # accommodation_type이 있는 mock request 생성
        room_data = {"accommodation": self.accommodation.id, **self.room_data}
        mock_request = type("Request", (), {"data": {"room": json.dumps(room_data)}})()

        data = {"type_name": "standard", "is_customized": False}
        serializer = RoomTypeSerializer(data=data, context={"request": mock_request})
        self.assertTrue(serializer.is_valid())

    def test_invalid_type_name(self):
        """잘못된 방 타입 이름으로 생성 시도"""
        # accommodation_type이 있는 mock request 생성
        room_data = {"accommodation": self.accommodation.id, **self.room_data}
        mock_request = type("Request", (), {"data": {"room": json.dumps(room_data)}})()

        data = {"type_name": "invalid_type", "is_customized": False}
        serializer = RoomTypeSerializer(data=data, context={"request": mock_request})
        self.assertFalse(serializer.is_valid())


class RoomImageSerializerTest(TestBase):
    def test_valid_image(self):
        """유효한 이미지 업로드"""
        image_content = (
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        )
        image = SimpleUploadedFile("test.gif", image_content, content_type="image/gif")
        data = {"room": self.room.id, "image": image}
        serializer = RoomImageSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_image_size(self):
        """너무 큰 이미지 업로드 시도"""
        large_image = SimpleUploadedFile("large.jpg", b"x" * (11 * 1024 * 1024), content_type="image/jpeg")  # 11MB
        data = {"room": self.room.id, "image": large_image}
        serializer = RoomImageSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)


class RoomInventorySerializerTest(TestBase):
    def test_valid_inventory(self):
        """유효한 인벤토리 생성"""
        data = {"count_room": 5}
        serializer = RoomInventorySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_room_count(self):
        """잘못된 방 개수로 생성 시도"""
        data = {"count_room": -1}
        serializer = RoomInventorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("count_room", serializer.errors)


class OptionSerializerTest(TestBase):
    def test_valid_option(self):
        """유효한 옵션 생성"""
        data = {"name": "룸서비스", "category": "extra", "is_custom": False}
        serializer = OptionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_category(self):
        """잘못된 카테고리로 옵션 생성 시도"""
        data = {"name": "test option", "category": "invalid_category", "is_custom": False}
        serializer = OptionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("category", serializer.errors)


class BedOptionSerializerTest(TestBase):
    def test_valid_bed_option(self):
        """유효한 침대 옵션 생성"""
        data = {"bed_type": "single", "quantity": 2}
        serializer = BedOptionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_none_bed_type(self):
        """침대 없음 옵션 테스트"""
        data = {"bed_type": "none", "quantity": 0}
        serializer = BedOptionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
