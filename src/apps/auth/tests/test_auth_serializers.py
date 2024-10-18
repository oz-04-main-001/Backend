from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.auth.serializers.auth_serializer import UserRegistrationSerializer
from apps.users.models import User  # type: ignore


class UserRegistrationSerializerTest(TestCase):

    def setUp(self):
        # 이미 존재하는 유저 데이터를 미리 생성해놓습니다.
        self.existing_user = User.objects.create_user(
            email="existing@example.com",
            password="password123",
            phone_number="01012345678",
        )

    def test_password_mismatch(self):
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "password123",
            "password2": "differentpassword",
            "birth_date": "1990-01-01",
            "gender": "M",
            "phone_number": "01098765432",
        }
        serializer = UserRegistrationSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_existing_email(self):
        data = {
            "email": "existing@example.com",  # 이미 존재하는 이메일
            "first_name": "John",
            "last_name": "Doe",
            "password": "password123",
            "password2": "password123",
            "birth_date": "1990-01-01",
            "gender": "M",
            "phone_number": "01098765432",
        }
        serializer = UserRegistrationSerializer(data=data)
        with self.assertRaises(ValidationError) as e:
            serializer.is_valid(raise_exception=True)
        self.assertIn("email", str(e.exception))

    def test_successful_registration(self):
        data = {
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "password123",
            "password2": "password123",
            "birth_date": "1990-01-01",
            "gender": "M",
            "phone_number": "01098765432",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
