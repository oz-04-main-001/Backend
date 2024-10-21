from django.core.management.base import BaseCommand
from faker import Faker
import random

from apps.common.choices import (
    GENDER_CHOICES,
    USER_TYPE_CHOICES,
    SOCIAL_LOGIN_CHOICES,
    VERIFICATION_STATUS_CHOICES,
    AMENITY_CHOICES_BY_CATEGORY,
    AMENITY_CATEGORIES_CHOICES,
    OPTION_CATEGORIES_CHOICES,
    OPTION_CHOICES_BY_CATEGORY,
)
from apps.users.models import User, BusinessUser
from apps.accommodations.models import Accommodation, AccommodationType, GPS_Info
from apps.rooms.models import Room, RoomType, RoomInventory
from apps.amenities.models import Amenity, AccommodationAmenity, Option, RoomOption


class Command(BaseCommand):
    help = "Generate fake data for all models"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # 1. User 데이터 생성
        self.generate_users(fake)

        # 2. BusinessUser 데이터 생성
        self.generate_business_users(fake)

        # 3. Accommodation 데이터 생성
        self.generate_accommodations(fake)

        # 4. Room 데이터 생성
        self.generate_rooms(fake)

        # 5. Amenity 및 옵션 생성
        self.generate_amenities(fake)

        print("All data generated successfully.")

    def generate_users(self, fake):
        print("Generating Users...")

        for _ in range(100):  # 유저 10명 생성
            user = User.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone_number=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                gender=random.choice([choice[0] for choice in GENDER_CHOICES]),  # 랜덤 성별 선택
                birth_date=fake.date_of_birth(),
                user_image=fake.image_url(),
                user_type=random.choice([choice[0] for choice in USER_TYPE_CHOICES]),  # 랜덤 유저 타입 선택
                social_id=fake.uuid4(),
                social_login=random.choice(
                    [choice[0] for choice in SOCIAL_LOGIN_CHOICES]
                ),  # 랜덤 소셜 로그인 타입 선택
                verified_email=fake.boolean(),
                is_active=fake.boolean(),
                created_at=fake.date_time(),
                updated_at=fake.date_time(),
                last_login=fake.date_time(),
                is_staff=fake.boolean(),
            )
            print(f"User created: {user.email}")

    def generate_business_users(self, fake):
        print("Generating Business Users...")

        # 'host' 타입의 User 중에서 BusinessUser가 없는 유저만 가져오기
        host_users = User.objects.filter(user_type="host").exclude(business_profile__isnull=False)

        for user in host_users:
            business_user = BusinessUser.objects.create(
                user=user,
                business_number=fake.bothify(text="#########")[:20],
                business_document=fake.file_name(),
                business_email=fake.email(),
                business_phonenumber=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                business_address=fake.address(),
                verification_status=random.choice([choice[0] for choice in VERIFICATION_STATUS_CHOICES]),
            )
            print(f"BusinessUser created: {business_user.business_email}")

    def generate_accommodations(self, fake):
        print("Generating Accommodations...")
        for _ in range(100):  # 숙소 10개 생성
            host = BusinessUser.objects.order_by("?").first()

            accommodation = Accommodation.objects.create(
                host=host,
                name=fake.company(),
                phone_number=host.business_phonenumber,
                description=fake.text(),
                rules=fake.text(),
                average_rating=random.uniform(1.0, 5.0),
                is_active=fake.boolean(),
                created_at=fake.date_time(),
                updated_at=fake.date_time(),
            )
            AccommodationType.objects.create(
                accommodation=accommodation, is_customized=fake.boolean(), type_name=fake.word()
            )
            GPS_Info.objects.create(
                accommodation=accommodation,
                city=fake.city(),
                states=fake.state(),
                road_name=fake.street_name(),
                address=fake.address(),
                latitude=fake.latitude(),
                longitude=fake.longitude(),
            )
            print(f"Accommodation created: {accommodation.name} with phone number {accommodation.phone_number}")

    def generate_rooms(self, fake):
        print("Generating Rooms...")
        for accommodation in Accommodation.objects.all():
            room = Room.objects.create(
                accommodation=accommodation,
                name=fake.word(),
                capacity=random.randint(1, 5),
                max_capacity=random.randint(5, 10),
                price=random.randint(100, 1000),
                stay_type=fake.boolean(),
                description=fake.text(),
                check_in_time=fake.time(),
                check_out_time=fake.time(),
                is_available=fake.boolean(),
            )
            RoomType.objects.create(room=room, is_customized=fake.boolean(), type_name=fake.word())
            RoomInventory.objects.create(room=room, count_room=random.randint(1, 5))
            print(f"Room created: {room.name} in {accommodation.name}")

    def generate_amenities(self, fake):
        print("Generating Amenities...")

        for accommodation in Accommodation.objects.all():
            for _ in range(7):
                category, _ = random.choice(AMENITY_CATEGORIES_CHOICES)

                if fake.boolean():
                    amenity_name, amenity_label = random.choice(AMENITY_CHOICES_BY_CATEGORY[category])
                    is_custom = True
                else:
                    amenity_name = fake.word()
                    is_custom = False

                amenity = Amenity.objects.create(
                    name=amenity_name,
                    category=category,
                    description=fake.text(),
                    is_custom=is_custom,
                )
                AccommodationAmenity.objects.create(
                    accommodation=accommodation, amenity=amenity, custom_value=fake.word()
                )
                print(f"Amenity {amenity.name} created for {accommodation.name}")

        for room in Room.objects.all():
            for _ in range(7):
                category, _ = random.choice(OPTION_CATEGORIES_CHOICES)

                if fake.boolean():
                    option_name, option_label = random.choice(OPTION_CHOICES_BY_CATEGORY[category])
                    is_custom = True
                else:
                    option_name = fake.word()
                    is_custom = False

                option = Option.objects.create(name=option_name, category=category, is_custom=is_custom)
                RoomOption.objects.create(room=room, option=option, custom_value=fake.word())
                print(f"Option {option.name} created for {room.name}")
