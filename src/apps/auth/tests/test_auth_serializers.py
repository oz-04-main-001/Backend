from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.auth.serializers.auth_serializer import (
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserEmailLookupSerializer,
    UserRegistrationSerializer,
)
from apps.auth.services.auth_service import UserAuthService

User = get_user_model()


class UserRegistrationSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "password123",
            "password2": "password123",
            "birth_date": "1990-01-01",
            "gender": "male",
            "phone_number": "010-1234-5678",  # 올바른 형식
        }
        self.invalid_phone_number_data = self.valid_data.copy()
        self.invalid_phone_number_data["phone_number"] = "01012345678"

        self.invalid_password_data = self.valid_data.copy()
        self.invalid_password_data["password2"] = "different_password"

        self.existing_user = User.objects.create_user(
            email="existing@example.com",
            first_name="Jane",
            last_name="Doe",
            phone_number="010-9876-5432",
            gender="F",
            birth_date="1985-05-05",
            password="password123",
        )

    def test_registration_serializer_with_valid_data(self):
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_registration_serializer_with_invalid_password(self):
        serializer = UserRegistrationSerializer(data=self.invalid_password_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_registration_serializer_existing_user(self):
        data_with_existing_email = self.valid_data.copy()
        data_with_existing_email["email"] = self.existing_user.email
        serializer = UserRegistrationSerializer(data=data_with_existing_email)

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("email", context.exception.detail)

        data_with_existing_phone = self.valid_data.copy()
        data_with_existing_phone["phone_number"] = self.existing_user.phone_number
        serializer = UserRegistrationSerializer(data=data_with_existing_phone)

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("phone_number", context.exception.detail)

    def test_registration_serializer_with_invalid_phone_number(self):
        serializer = UserRegistrationSerializer(data=self.invalid_phone_number_data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Phone number must be in the format 010-1234-5678.", str(context.exception))


class LoginSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Jane",
            last_name="Doe",
            phone_number="010-9876-5432",
            gender="F",
            birth_date="1985-05-05",
            password="password123",
        )
        self.valid_data = {"email": "test@example.com", "password": "password123"}
        self.invalid_data = {"email": "test@example.com", "password": "wrongpassword"}

    def test_login_serializer_with_valid_data(self):
        serializer = LoginSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_login_serializer_with_invalid_data(self):
        serializer = LoginSerializer(data=self.invalid_data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Invalid email or password.", str(context.exception))


class UserEmailLookupSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
            password="password123",
        )
        self.valid_data = {"phone_number": "010-1234-5678", "full_name": "John Doe"}
        self.invalid_phone_number_data = {"phone_number": "01012345678", "full_name": "John Doe"}
        self.non_existent_user_data = {"phone_number": "010-9999-9999", "full_name": "Jane Doe"}

        # 모의 UserAuthService
        self.user_auth_service = UserAuthService()

    def test_email_lookup_serializer_with_valid_data(self):
        serializer = UserEmailLookupSerializer(data=self.valid_data)
        if not serializer.is_valid():
            print(serializer.errors)  # 오류 출력
        self.assertTrue(serializer.is_valid())

    def test_email_lookup_serializer_with_invalid_phone_number(self):
        serializer = UserEmailLookupSerializer(data=self.invalid_phone_number_data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Phone number must be in the format 010-1234-5678.", str(context.exception))

    def test_email_lookup_serializer_with_non_existent_user(self):
        serializer = UserEmailLookupSerializer(data=self.non_existent_user_data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("No user found with this phone number and full name.", str(context.exception))


class PasswordResetRequestSerializerTest(TestCase):
    def setUp(self):
        self.existing_user_email = "existing@example.com"
        self.non_existing_user_email = "nonexisting@example.com"

        User.objects.create_user(
            email=self.existing_user_email,
            first_name="John",
            last_name="Doe",
            phone_number="010-1234-5678",
            gender="male",
            birth_date="1990-01-01",
            password="password123",
        )

    def test_validate_email_with_existing_user(self):
        serializer = PasswordResetRequestSerializer(data={"email": self.existing_user_email})
        self.assertTrue(serializer.is_valid())

    def test_validate_email_with_non_existing_user(self):
        serializer = PasswordResetRequestSerializer(data={"email": self.non_existing_user_email})
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)

        self.assertIn("No user is associated with this email.", str(context.exception))


class PasswordResetSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "password": "newpassword123",
            "password2": "newpassword123",
        }
        self.invalid_data = {
            "password": "newpassword123",
            "password2": "differentpassword",
        }

    def test_password_reset_serializer_with_valid_data(self):
        serializer = PasswordResetSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_password_reset_serializer_with_mismatched_passwords(self):
        serializer = PasswordResetSerializer(data=self.invalid_data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("The two password fields didn’t match.", str(context.exception))
