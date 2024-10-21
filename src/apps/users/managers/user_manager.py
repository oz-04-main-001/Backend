from typing import TYPE_CHECKING, Any, Optional

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist

from apps.users.conditions.user_get_condtions import email_or_phone_condition

if TYPE_CHECKING:
    from apps.users.models import User  # type: ignore


class UserManager(BaseUserManager):
    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        gender: str,
        birth_date: str,
        password: str | None = None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            gender=gender,
            birth_date=birth_date,
            **extra_fields,
        )

        user.verified_email = True
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "admin")

        first_name = extra_fields.pop("first_name", "Admin")
        last_name = extra_fields.pop("last_name", "User")
        phone_number = extra_fields.pop("phone_number", "")
        gender = extra_fields.pop("gender", "other")
        birth_date = extra_fields.pop("birth_date", "1900-01-01")

        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            gender=gender,
            birth_date=birth_date,
            password=password,
            **extra_fields,
        )

    def get_user_by_email_or_phone(self, email: str, phone_number: str) -> "User | None":
        return self.filter(email_or_phone_condition(email=email, phone_number=phone_number)).first()

    def email_exists(self, email: str) -> bool:
        return self.filter(email=email).exists()

    def get_user_by_email(self, email: str) -> "User | None":
        try:
            return self.get(email=email)
        except ObjectDoesNotExist:
            return None

    def get_user_by_id(self, id: int) -> "User | None":
        try:
            return self.get(id=id)
        except ObjectDoesNotExist:
            return None

    def deactivate_user(self, user) -> "User":
        user.is_active = False
        user.save(using=self._db)
        return user

    def get_user_by_phone_and_name(self, phone_number: str, first_name: str, last_name: str) -> "User | None":
        try:
            return self.get(first_name=first_name, last_name=last_name, phone_number=phone_number)
        except ObjectDoesNotExist:
            return None
