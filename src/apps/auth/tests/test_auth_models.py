from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from apps.users.models import User


class UserManagerTest(TestCase):
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

    def test_create_user(self):
        user = User.objects.create_user(
            email="newuser@example.com",
            first_name="Jane",
            last_name="Smith",
            phone_number="010-9876-5432",
            gender="female",
            birth_date="1995-05-05",
            password="password456",
        )
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("password456"))

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword",
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_get_user_by_email(self):
        user = User.objects.get_user_by_email("test@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_get_user_by_email_not_found(self):
        user = User.objects.get_user_by_email("notfound@example.com")
        self.assertIsNone(user)

    def test_get_user_by_email_or_phone(self):
        user = User.objects.get_user_by_email_or_phone(email="nonexistent@example.com", phone_number="010-1234-5678")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_get_user_by_id(self):
        user = User.objects.get_user_by_id(self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_get_user_by_id_not_found(self):
        user = User.objects.get_user_by_id(9999)
        self.assertIsNone(user)

    def test_deactivate_user(self):
        deactivated_user = User.objects.deactivate_user(self.user)
        self.assertFalse(deactivated_user.is_active)

    def test_get_user_by_phone(self):
        user = User.objects.get_user_by_phone(phone_number="010-1234-5678")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_get_user_by_phone_invalid(self):
        user = User.objects.get_user_by_phone(phone_number="010-9999-9999")
        self.assertIsNone(user)

    def test_user_not_found(self):
        user = User.objects.get_user_by_email("notfound@example.com")
        self.assertIsNone(user)
