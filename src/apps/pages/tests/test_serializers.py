# from django.test import TestCase
# from django.utils import timezone
#
# from apps.accommodations.models import Accommodation, Accommodation_Image, GPS_Info
# from apps.rooms.models import Room
# from apps.pages.serializers.accommodation_serializer import AccommodationDetailSerializer
# from apps.pages.serializers.room_serializer import RoomSerializer
# from apps.pages.serializers.main_serializer import MainPageSerializer
# from apps.users.models import User, BusinessUser, WithdrawManager
#
#
# class HotelDetailSerializerTest(TestCase):
#     def setUp(self):
#
#
#         self.user = User.objects.create(
#             first_name="John",
#             last_name="Doe",
#             email="john.doe@example.com",
#             phone_number="010-1234-5678",
#             gender="male",  # GENDER_CHOICES에 있는 값
#             birth_date="1990-01-01",
#             user_image="profile.jpg",
#             user_type="guest",  # USER_TYPE_CHOICES에 있는 값
#             social_id="1234567890",
#             social_login="google",  # SOCIAL_LOGIN_CHOICES에 있는 값
#             verified_email=True,
#             is_active=True,
#             last_login=timezone.now(),
#         )
#
#         # 사업 사용자 생성
#         self.business_user = BusinessUser.objects.create(
#             user=self.user,
#             business_number="1234567890",
#             business_document="business_documents/sample_document.pdf",
#             business_email="business@example.com",
#             business_phonenumber="02-9876-5432",
#             business_address="123 Business St",
#             verified_at=None,
#             verification_status="pending"
#         )
#
#         # # 철회 관리자 생성
#         # self.withdraw_manager = WithdrawManager.objects.create(
#         #     user=self.user,
#         #     withdraw_reason="No longer using the service"
#         # )
#         # 호텔 기본 정보 설정
#         self.accommodation = Accommodation.objects.create(
#             host=self.business_user,
#             name="Test Hotel",
#             phone_number="123-456-7890",
#             description="A Luxuious test hotel",
#             rules="No smoking, No pets",
#             average_rating=1.0,
#             is_active=True,
#             created_at="2024-10-01",
#             updated_at="2024-10-24",
#         )
#
#         # 호텔 주소 정보 설정
#         self.gps_info = GPS_Info.objects.create(
#             accommodation=self.accommodation,
#             city="Test City",
#             states="Test State",
#             road_name="123 Test Road",
#             address="4567",
#         )
#
#         # 호텔 이미지 설정
#         self.hotel_img = Accommodation_Image.objects.create(
#             accommodation=self.accommodation,
#             image="test_image.jpg",
#         )
#
#         # 호텔 객실 설정
#         self.room1 = Room.objects.create(
#             accommodation=self.accommodation,
#             name="Standard Room",
#             price=100.00,
#         )
#         self.room2 = Room.objects.create(
#             accommodation=self.accommodation,
#             name="Deluxe Room",
#             price=200.00,
#         )
#
#
#     def test_hotel_detail_serializer(self):
#         serializer = AccommodationDetailSerializer(self.accommodation)
#         data = serializer.data
#
#         self.assertEqual(data["name"], self.accommodation.name)
#         self.assertEqual(data["phone_number"], self.accommodation.phone_number)
#         self.assertEqual(data["address"], "Test City Test State 123 Test Road 4567")
#         self.assertEqual(data["hotel_img"], ["test_image.jpg"])
#         self.assertEqual(data["min_price"], 100.00)
#         self.assertEqual(len(data["rooms"]), 2)
#         self.assertEqual(data["rooms"][0]["name"], "Standard Room")
#         self.assertEqual(data["rooms"][1]["name"], "Deluxe Room")
#         self.assertEqual(data["description"], self.accommodation.description)
#         self.assertEqual(data["rules"], self.accommodation.rules)
#         self.assertEqual(data["average_rating"], round(self.accommodation.average_rating, 1))  # 반올림 적용
#         self.assertEqual(data["is_active"], self.accommodation.is_active)
#
#
# class MainPageSerializerTest(TestCase):
#     def setUp(self):
#         self.accommodation = Accommodation.objects.create(name="Test Hotel")
#         self.room1 = Room.objects.create(
#             accommodation=self.accommodation,
#             name="Standard Room",
#             price=100.00,
#         )
#         self.hotel_img = Accommodation_Image.objects.create(
#             accommodation=self.accommodation,
#             image="test_image.jpg",
#         )
#
#     def test_main_page_serializer(self):
#         serializer = MainPageSerializer(self.accommodation)
#         data = serializer.data
#
#         self.assertEqual(data["name"], "Test Hotel")
#         self.assertEqual(data["rooms"], 100.00)
#         self.assertEqual(data["hotel_img"], "test_image.jpg")
#
#
# class RoomSerializerTest(TestCase):
#     def setUp(self):
#         self.accommodation = Accommodation.objects.create(name="Test Hotel")
#         self.room = Room.objects.create(
#             accommodation=self.accommodation,
#             name="Standard Room",
#             capacity=2,
#             max_capacity=4,
#             description="A comfortable room",
#             price=150.00,
#             stay_type="nightly",
#             check_in_time="14:00",
#             check_out_time="12:00"
#         )
#
#     def test_room_serializer(self):
#         serializer = RoomSerializer(self.room)
#         data = serializer.data
#
#         self.assertEqual(data["accommodation_name"], "Test Hotel")
#         self.assertEqual(data["name"], "Standard Room")
#         self.assertEqual(data["capacity"], 2)
#         self.assertEqual(data["max_capacity"], 4)
#         self.assertEqual(data["description"], "A comfortable room")
#         self.assertEqual(data["price"], 150.00)
#         self.assertEqual(data["stay_type"], "nightly")
#         self.assertEqual(data["check_in_time"], "14:00")
#         self.assertEqual(data["check_out_time"], "12:00")
