from django.test import TestCase
from rest_framework.exceptions import NotFound, ValidationError

from apps.auth.services.auth_service import UserAuthService
from apps.users.models import User, WithdrawManager


class UserAuthServiceTest(TestCase):
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
        self.user_auth_service = UserAuthService()

    def test_create_user(self):
        validated_data = {
            "email": "newuser@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "010-9876-5432",
            "gender": "female",
            "birth_date": "1995-05-05",
            "password": "password456",
        }
        user = self.user_auth_service.create_user(validated_data)
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("password456"))

    def test_deactivate_user(self):
        self.user_auth_service.deactivate_user(self.user)
        self.assertFalse(self.user.is_active)

    def test_find_user_by_phone(self):
        user = self.user_auth_service.find_user_by_phone(phone_number="010-1234-5678")
        self.assertEqual(user.email, "test@example.com")

        user_not_found = self.user_auth_service.find_user_by_phone(phone_number="010-9999-9999")
        self.assertIsNone(user_not_found)

    def test_get_user_by_email(self):
        user = self.user_auth_service.get_user_by_email(email="test@example.com")
        self.assertEqual(user.email, "test@example.com")

        with self.assertRaises(NotFound):
            self.user_auth_service.get_user_by_email(email="nonexistent@example.com")

    def test_set_user_password(self):
        new_password = "newpassword123"
        self.user_auth_service.set_user_password(self.user, new_password)
        self.assertTrue(self.user.check_password(new_password))

    def test_create_withdraw_record(self):
        withdraw_reason = "User requested withdrawal"
        self.user_auth_service.create_withdraw_record(user=self.user, withdraw_reason=withdraw_reason)

        withdraw_record = WithdrawManager.objects.filter(user=self.user).first()
        self.assertIsNotNone(withdraw_record)
        self.assertEqual(withdraw_record.withdraw_reason, withdraw_reason)

    def test_check_if_email_exists(self):
        self.assertTrue(self.user_auth_service.check_if_email_exists(email="test@example.com"))
        self.assertFalse(self.user_auth_service.check_if_email_exists(email="nonexistent@example.com"))

    def test_validate_email_in_session(self):
        with self.assertRaises(ValidationError) as context:
            self.user_auth_service.validate_email_in_session(email="")

        self.assertIn("No email found.", str(context.exception))

    def test_validate_user_data_in_session(self):
        with self.assertRaises(ValidationError) as context:
            self.user_auth_service.validate_user_data_in_session(user_data={})

        self.assertIn("User data not found in session.", str(context.exception))
