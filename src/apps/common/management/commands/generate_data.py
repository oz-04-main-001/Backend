import random
from datetime import datetime, time, timedelta

from django.contrib.auth.hashers import make_password
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.accommodations.models import (
    Accommodation,
    AccommodationType,
    GPS_Info,
    RefundPolicy,
)
from apps.amenities.models import AccommodationAmenity, Amenity, Option, RoomOption
from apps.bookings.models import Booking
from apps.common.choices import (
    AMENITY_CATEGORIES_CHOICES,
    AMENITY_CHOICES_BY_CATEGORY,
    BOOKING_STATUS_CHOICES,
    GENDER_CHOICES,
    OPTION_CATEGORIES_CHOICES,
    OPTION_CHOICES_BY_CATEGORY,
    SOCIAL_LOGIN_CHOICES,
    USER_TYPE_CHOICES,
    VERIFICATION_STATUS_CHOICES,
)
from apps.rooms.models import Room, Room_Image, RoomInventory, RoomType
from apps.users.models import BusinessUser, User


class Command(BaseCommand):
    help = "Generate fake data for all models"

    def handle(self, *args, **kwargs):
        fake = Faker("ko_KR")

        # 1. 슈퍼유저 생성 및 BusinessUser 프로필 추가
        self.create_superuser_and_business_profile(fake)

        # 2. User 데이터 생성
        self.generate_users(fake)

        # 3. BusinessUser 데이터 생성
        self.generate_business_users(fake)

        # 4. Accommodation 데이터 생성
        self.generate_accommodations(fake)

        # 5. Room 데이터 생성
        self.generate_rooms(fake)

        # 6. Amenity 및 옵션 생성
        self.generate_amenities(fake)

        # 7.새로운 Booking 데이터 생성
        self.generate_bookings(fake)

        print("All data generated successfully.")

    def create_superuser_and_business_profile(self, fake):
        print("Creating superuser and business profile...")

        superuser = User.objects.create_user(
            email="admin1@naver.com",
            password="12345678",
            is_superuser=True,
            first_name="Admin",
            last_name="User",
            phone_number="010-1234-5678",
            gender="male",
            birth_date=fake.date_of_birth(minimum_age=25, maximum_age=55),
            user_type="host",
            social_login="email",
            verified_email=True,
            is_active=True,
            is_staff=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        business_user = BusinessUser.objects.create(
            user=superuser,
            business_number="1234567890",
            business_document="business_doc.pdf",
            business_email="admin_business@naver.com",
            business_phonenumber="011-1234-5678",
            business_address=fake.address(),
            verification_status="verified",
        )

        print(f"Superuser created: {superuser.email}")
        print(f"BusinessUser profile created for superuser: {business_user.business_email}")

        # 슈퍼유저의 숙소 생성
        self.create_accommodation_for_superuser(fake, business_user)

    def create_accommodation_for_superuser(self, fake, business_user):
        accommodation = Accommodation.objects.create(
            host=business_user,
            name="Admin's Luxury Hotel",
            phone_number=business_user.business_phonenumber,
            description=fake.paragraph(),
            rules="No smoking, No pets, Check-in after 2 PM, Check-out before 11 AM",
            average_rating=4.8,
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        AccommodationType.objects.create(accommodation=accommodation, is_customized=False, type_name="Hotel")

        GPS_Info.objects.create(
            accommodation=accommodation,
            city="서울",
            states="서울특별시",
            road_name="테헤란로",
            address="서울특별시 강남구 테헤란로 123",
            location=Point(127.0395, 37.5011),  # 서울 강남구의 대략적인 좌표
        )

        RefundPolicy.objects.create(
            accommodation=accommodation,
            seven_days_before=100,
            five_days_before=80,
            three_days_before=50,
            one_day_before=20,
            same_day=0,
        )

        print(f"Accommodation created for superuser: {accommodation.name}")

        # 슈퍼유저의 숙소에 대한 객실 생성
        self.create_rooms_for_superuser_accommodation(fake, accommodation)

    def create_rooms_for_superuser_accommodation(self, fake, accommodation):
        room_types = ["Standard", "Deluxe", "Suite", "Executive"]

        for room_type in room_types:
            room = Room.objects.create(
                accommodation=accommodation,
                name=f"{room_type} Room",
                capacity=random.randint(2, 4),
                max_capacity=random.randint(4, 6),
                price=random.randint(100000, 500000),
                stay_type=True,
                description=fake.paragraph(),
                check_in_time=time(14, 0),
                check_out_time=time(11, 0),
                is_available=True,
            )

            RoomType.objects.create(room=room, is_customized=False, type_name=room_type)

            RoomInventory.objects.create(room=room, count_room=random.randint(5, 20))

            # 객실 이미지 추가
            for i in range(3):
                Room_Image.objects.create(
                    room=room,
                    image=f"room_images/{room.name.lower().replace(' ', '_')}_{i+1}.jpg",
                    is_representative=(i == 0),
                )

            print(f"Room created for superuser's accommodation: {room.name}")

    def generate_users(self, fake):
        print("Generating Users...")

        for _ in range(30):
            user = User.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password=make_password(fake.password()),
                phone_number=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                gender=random.choice([choice[0] for choice in GENDER_CHOICES]),
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=80),
                user_image=f"user_images/{fake.uuid4()}.jpg",
                user_type=random.choice([choice[0] for choice in USER_TYPE_CHOICES]),
                social_id=fake.uuid4() if random.choice([True, False]) else None,
                social_login=random.choice([choice[0] for choice in SOCIAL_LOGIN_CHOICES]),
                verified_email=fake.boolean(chance_of_getting_true=80),
                is_active=fake.boolean(chance_of_getting_true=95),
                created_at=fake.date_time_between(
                    start_date="-2y", end_date="now", tzinfo=timezone.get_current_timezone()
                ),
                updated_at=fake.date_time_between(
                    start_date="-1y", end_date="now", tzinfo=timezone.get_current_timezone()
                ),
                last_login=fake.date_time_between(
                    start_date="-1m", end_date="now", tzinfo=timezone.get_current_timezone()
                ),
                is_staff=fake.boolean(chance_of_getting_true=5),
            )
            print(f"User created: {user.email}")

    def generate_business_users(self, fake):
        print("Generating Business Users...")

        host_users = User.objects.filter(user_type="host").exclude(business_profile__isnull=False)

        for user in host_users:
            business_user = BusinessUser.objects.create(
                user=user,
                business_number=fake.unique.random_number(digits=10),
                business_document=f"business_docs/{fake.uuid4()}.pdf",
                business_email=fake.company_email(),
                business_phonenumber=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                business_address=fake.address(),
                verification_status=random.choice([choice[0] for choice in VERIFICATION_STATUS_CHOICES]),
            )
            print(f"BusinessUser created: {business_user.business_email}")

    def generate_accommodations(self, fake):
        print("Generating Accommodations...")
        accommodation_types = ["Hotel", "Motel", "Resort", "Pension", "Guesthouse"]

        for _ in range(100):
            host = BusinessUser.objects.order_by("?").first()

            accommodation = Accommodation.objects.create(
                host=host,
                name=fake.company() + " " + random.choice(["Hotel", "Resort", "Inn", "Suites"]),
                phone_number=host.business_phonenumber,
                description=fake.paragraph(),
                rules=fake.paragraph(),
                average_rating=round(random.uniform(3.0, 5.0), 1),
                is_active=fake.boolean(chance_of_getting_true=90),
                created_at=fake.date_time_between(
                    start_date="-2y", end_date="now", tzinfo=timezone.get_current_timezone()
                ),
                updated_at=fake.date_time_between(
                    start_date="-1y", end_date="now", tzinfo=timezone.get_current_timezone()
                ),
            )

            AccommodationType.objects.create(
                accommodation=accommodation,
                is_customized=fake.boolean(chance_of_getting_true=20),
                type_name=random.choice(accommodation_types),
            )

            GPS_Info.objects.create(
                accommodation=accommodation,
                city=fake.city(),
                states=fake.administrative_unit(),  # state() 대신 administrative_unit() 사용
                road_name=fake.street_name(),
                address=fake.address(),
                location=Point(
                    random.uniform(124.0, 132.0),  # 경도 (longitude)
                    random.uniform(33.0, 38.0),  # 위도 (latitude)
                ),
            )

            RefundPolicy.objects.create(
                accommodation=accommodation,
                seven_days_before=random.choice([100, 90, 80]),
                five_days_before=random.choice([80, 70, 60]),
                three_days_before=random.choice([50, 40, 30]),
                one_day_before=random.choice([30, 20, 10]),
                same_day=random.choice([0, 10]),
            )

            print(f"Accommodation created: {accommodation.name} with phone number {accommodation.phone_number}")

    def generate_rooms(self, fake):
        print("Generating Rooms...")
        room_types = ["Standard", "Deluxe", "Suite", "Family", "Single", "Double"]

        for accommodation in Accommodation.objects.all():
            for _ in range(random.randint(3, 5)):
                # 체크인 시간을 오후 2시에서 4시 사이로 설정
                check_in_hour = random.randint(14, 16)
                check_in_time = time(hour=check_in_hour, minute=0)

                # 체크아웃 시간을 오전 10시에서 12시 사이로 설정
                check_out_hour = random.randint(10, 12)
                check_out_time = time(hour=check_out_hour, minute=0)

                room = Room.objects.create(
                    accommodation=accommodation,
                    name=fake.word().capitalize() + " " + random.choice(room_types),
                    capacity=random.randint(1, 4),
                    max_capacity=random.randint(4, 8),
                    price=random.randint(50000, 500000),
                    stay_type=random.choice([True, False]),
                    description=fake.paragraph(),
                    check_in_time=check_in_time,
                    check_out_time=check_out_time,
                    is_available=fake.boolean(chance_of_getting_true=90),
                )

                RoomType.objects.create(
                    room=room,
                    is_customized=fake.boolean(chance_of_getting_true=20),
                    type_name=random.choice(room_types),
                )

                RoomInventory.objects.create(
                    room=room,
                    count_room=random.randint(1, 20),
                )

                # 객실 이미지 추가
                for i in range(3):
                    Room_Image.objects.create(
                        room=room,
                        image=f"room_images/{room.name.lower().replace(' ', '_')}_{i+1}.jpg",
                        is_representative=(i == 0),
                    )

                print(f"Room created: {room.name} in {accommodation.name}")

    def generate_amenities(self, fake):
        print("Generating Amenities...")

        Amenity.objects.all().delete()
        Option.objects.all().delete()

        for accommodation in Accommodation.objects.all():
            for category, _ in AMENITY_CATEGORIES_CHOICES:
                for _ in range(random.randint(2, 5)):
                    if random.choice([True, False]):
                        amenity_name, _ = random.choice(AMENITY_CHOICES_BY_CATEGORY[category])
                        is_custom = False
                    else:
                        amenity_name = fake.word().capitalize()
                        is_custom = True

                    amenity, _ = Amenity.objects.get_or_create(
                        name=amenity_name,
                        category=category,
                        defaults={
                            "description": fake.sentence(),
                            "is_custom": is_custom,
                        },
                    )

                    AccommodationAmenity.objects.get_or_create(
                        accommodation=accommodation,
                        amenity=amenity,
                        defaults={
                            "custom_value": random.randint(2, 5) if is_custom else 1,
                        },
                    )

                print(f"Amenities created for {accommodation.name}")

        for room in Room.objects.all():
            for category, _ in OPTION_CATEGORIES_CHOICES:
                for _ in range(random.randint(2, 5)):
                    if random.choice([True, False]):
                        option_name, _ = random.choice(OPTION_CHOICES_BY_CATEGORY[category])
                        is_custom = False
                    else:
                        option_name = fake.word().capitalize()
                        is_custom = True

                    option, _ = Option.objects.get_or_create(
                        name=option_name, category=category, defaults={"is_custom": is_custom}
                    )

                    RoomOption.objects.get_or_create(
                        room=room,
                        option=option,
                        defaults={
                            "custom_value": random.randint(2, 5) if is_custom else 1,
                        },
                    )

                print(f"Options created for {room.name}")

    def generate_bookings(self, fake):
        print("Generating Bookings...")

        rooms = Room.objects.all()
        guests = User.objects.filter(user_type="guest")  # guest 사용자만 선택
        superuser_rooms = rooms.filter(accommodation__host__user__is_superuser=True)

        if not rooms.exists() or not guests.exists():
            print("No rooms or guests available for creating bookings.")
            return

        # 일반 사용자 방에 대한 예약 생성
        for _ in range(20):  # 원하는 예약 개수만큼 반복
            room = random.choice(rooms)
            guest = random.choice(guests)
            self.create_booking(fake, room, guest)

        # 슈퍼유저 방에 대한 추가 예약 생성
        for room in superuser_rooms:
            for _ in range(random.randint(1, 3)):  # 슈퍼유저 방에 대해 1~3개의 추가 예약 생성
                guest = random.choice(guests)
                self.create_booking(fake, room, guest)

    # 예약 생성을 위한 공통 함수
    def create_booking(self, fake, room, guest):
        guests_count = random.randint(1, room.capacity)
        total_price = room.price * guests_count
        check_in_date = timezone.now() + timedelta(days=random.randint(1, 30))
        check_out_date = check_in_date + timedelta(days=random.randint(1, 7))

        # 예약 생성
        booking, created = Booking.objects.get_or_create(
            room=room,
            guest=guest,
            check_in_datetime=check_in_date,
            check_out_datetime=check_out_date,
            defaults={
                "total_price": total_price,
                "status": random.choice([status[0] for status in BOOKING_STATUS_CHOICES]),
                "request": fake.text(max_nb_chars=100),
                "guests_count": guests_count,
                "booker_name": f"{guest.last_name}{guest.first_name}",
                "booker_phone_number": fake.phone_number(),
            },
        )

        if created:
            print(f"Booking created for {booking.booker_name} in room {room.name} with status {booking.status}")
        else:
            print(f"Booking for {booking.booker_name} in room {room.name} already exists, skipping creation.")
