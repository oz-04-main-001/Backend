# apps/core/test_base.py
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.accommodations.models import Accommodation, AccommodationType
from apps.amenities.models import Option, RoomOption
from apps.rooms.models import Room, RoomInventory, RoomType
from apps.users.models import BusinessUser

User = get_user_model()


class TestBase(APITestCase):
    def setUp(self):
        # 테스트 문서 파일 생성
        self.test_document = SimpleUploadedFile(
            name="business_doc.pdf", content=b"test document content", content_type="application/pdf"
        )

        # 사용자 및 비즈니스 사용자 생성
        self.user = User.objects.create_superuser(
            email="test@test.com", password="testpass123", phone_number="010-1234-5678"
        )
        self.host = BusinessUser.objects.create(
            user=self.user, business_document=self.test_document, business_number="123-45-67890"
        )

        # 숙소 데이터 설정
        self.accommodation_data = {
            "name": "Test Accommodation",
            "phone_number": "02-1234-5678",
            "description": "Test Description that is long enough",
            "rules": "Test Rules that are clear",
            "accommodation_type": {"type_name": "Hotel", "is_customized": False},
            "gps_info": {
                "city": "Seoul",
                "states": "Seoul",
                "road_name": "Gangnam-daero",
                "address": "123 Gangnam-daero",
                "location": {"type": "Point", "coordinates": [127.0295, 37.4979]},
            },
        }

        # 숙소 생성
        self.accommodation = Accommodation.objects.create(
            name=self.accommodation_data["name"],
            host=self.host,
            phone_number=self.host.user.phone_number,
            description=self.accommodation_data["description"],
            rules=self.accommodation_data["rules"],
        )

        # 숙소 타입 생성
        self.accommodation_type = AccommodationType.objects.create(
            type_name="호텔", is_customized=False, accommodation=self.accommodation
        )

        self.room_data = {
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

        # 룸 생성용 데이터 (모델 생성용)

        # 룸 생성
        self.room = Room.objects.create(
            accommodation=self.accommodation, **self.room_data  # 객체로 전달  # ID가 없는 데이터 사용
        )

        # 룸 타입 생성
        self.room_type = RoomType.objects.create(type_name="Standard", is_customized=False, room=self.room)
        self.test_images = []
        image_content = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )  # 1x1 GIF 이미지

        for i in range(3):
            self.test_images.append(
                SimpleUploadedFile(name=f"test_image_{i}.gif", content=image_content, content_type="image/gif")
            )

        # 룸 인벤토리 생성
        self.room_inventory = RoomInventory.objects.create(room=self.room, count_room=1)

        # 침대 옵션 생성 및 연결
        self.bed_options_data = [{"bed_type": "king", "quantity": 2}, {"bed_type": "single", "quantity": 1}]

        # 침대 옵션 생성 및 RoomOption으로 연결
        self.bed_options = []
        for bed_data in self.bed_options_data:
            # Option 생성
            option = Option.objects.create(name=bed_data["bed_type"], category="bed", is_custom=False)
            # RoomOption으로 연결 (custom_value 없이)
            room_option = RoomOption.objects.create(
                room=self.room, option=option, custom_value=None  # custom_value는 사용하지 않음
            )
            self.bed_options.append(
                {
                    "option": option,
                    "room_option": room_option,
                    "quantity": bed_data["quantity"],  # quantity는 테스트용으로만 저장
                }
            )

        # 기타 옵션 생성
        self.bathroom_option = Option.objects.create(name="룸서비스", category="extra", is_custom=False)

        self.view_option = Option.objects.create(name="발코니", category="extra", is_custom=False)

        # 커스텀 옵션 생성
        self.custom_option = Option.objects.create(name="테스트용", category="extra", is_custom=True)

        # 기타 옵션들 Room과 연결
        self.room_options = [
            RoomOption.objects.create(room=self.room, option=self.bathroom_option),
            RoomOption.objects.create(room=self.room, option=self.view_option),
            RoomOption.objects.create(
                room=self.room,
                option=self.custom_option,
            ),
        ]

        # 테스트를 위한 전체 옵션 데이터
        self.option_data = {
            "bed_options": self.bed_options_data,  # 침대 옵션
            "options": {  # 기타 옵션
                "new": [{"name": "테스트용", "category": "extra", "is_custom": True}],
                "default": [{"option_id": self.bathroom_option.id}, {"option_id": self.view_option.id}],
            },
        }

        self.create_room_data = {
            "room": self.room_data,
            "room_type": {
                "type_name": self.room_type.type_name,
            },
            "images": self.test_images,
            "inventory": {"count_room": self.room_inventory.count_room},
            "bed_options": self.bed_options_data,
            "options": {
                "new": [{"name": "custom feature", "category": "extra", "is_custom": True}],
                "default": [{"option_id": self.bathroom_option.id}, {"option_id": self.view_option.id}],
            },
        }

        self.client.force_authenticate(user=self.user)
