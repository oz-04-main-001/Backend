# apps/rooms/tests/test_models.py
from django.db.utils import IntegrityError

from apps.amenities.models import Option, RoomOption
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.rooms.tests.rooms_base import TestBase


class RoomModelTest(TestBase):
    def test_create_room_with_valid_data(self):
        """유효한 데이터로 Room 생성 테스트"""
        new_room = Room.objects.create(accommodation=self.accommodation, **self.room_data)

        self.assertEqual(new_room.name, self.room_data["name"])
        self.assertEqual(new_room.capacity, self.room_data["capacity"])
        self.assertEqual(new_room.price, self.room_data["price"])
        self.assertEqual(new_room.accommodation, self.accommodation)


class RoomTypeModelTest(TestBase):
    def test_create_room_type(self):
        """RoomType 생성 테스트"""
        new_room = Room.objects.create(accommodation=self.accommodation, **self.room_data)

        room_type = RoomType.objects.create(room=new_room, type_name="Deluxe", is_customized=False)

        self.assertEqual(room_type.type_name, "Deluxe")
        self.assertFalse(room_type.is_customized)

    def test_unique_room_type_per_room(self):
        """한 방에 대한 RoomType 중복 생성 시도"""
        new_room = Room.objects.create(accommodation=self.accommodation, **self.room_data)

        RoomType.objects.create(room=new_room, type_name="Deluxe", is_customized=False)

        with self.assertRaises(IntegrityError):
            RoomType.objects.create(room=new_room, type_name="Suite", is_customized=False)


class RoomImageModelTest(TestBase):
    def test_create_room_image(self):
        """Room_Image 생성 테스트"""
        image = Room_Image.objects.create(room=self.room, image=self.test_images[0], is_representative=True)

        self.assertTrue(image.is_representative)
        self.assertEqual(image.room, self.room)
        self.assertIsNotNone(image.image)


class RoomInventoryModelTest(TestBase):
    def test_create_room_inventory(self):
        """RoomInventory 생성 테스트"""
        new_room = Room.objects.create(accommodation=self.accommodation, **self.room_data)

        inventory = RoomInventory.objects.create(room=new_room, count_room=5)

        self.assertEqual(inventory.count_room, 5)
        self.assertEqual(inventory.room, new_room)

    def test_unique_room_inventory_per_room(self):
        """한 방에 대한 RoomInventory 중복 생성 시도"""
        new_room = Room.objects.create(accommodation=self.accommodation, **self.room_data)

        RoomInventory.objects.create(room=new_room, count_room=5)

        with self.assertRaises(IntegrityError):
            RoomInventory.objects.create(room=new_room, count_room=3)


class RoomOptionModelTest(TestBase):
    def test_create_room_option(self):
        """RoomOption 생성 테스트"""
        option = Option.objects.create(name="new_option", category="extra", is_custom=False)

        room_option = RoomOption.objects.create(room=self.room, option=option)

        self.assertEqual(room_option.room, self.room)
        self.assertEqual(room_option.option, option)

    def test_unique_room_option_combination(self):
        """같은 방과 옵션 조합의 중복 생성 시도"""
        option = Option.objects.create(name="test_option", category="extra", is_custom=False)

        RoomOption.objects.create(room=self.room, option=option)

        with self.assertRaises(IntegrityError):
            RoomOption.objects.create(room=self.room, option=option)
