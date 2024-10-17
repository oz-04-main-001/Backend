from django.contrib.auth.base_user import BaseUserManager

from apps.users.conditions.user_get_condtions import email_or_phone_condition


class UserManager(BaseUserManager):
    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        gender: str,
        birth_date: str,
        password: str = None,
        **extra_fields
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
            birth_date=birth_date,  # birth_date 추가
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "admin")

        return self.create_user(
            email=email,
            first_name=extra_fields.get("first_name", "Admin"),
            last_name=extra_fields.get("last_name", "User"),
            phone_number=extra_fields.get("phone_number", ""),
            gender=extra_fields.get("gender", "other"),
            birth_date=extra_fields.get("birth_date", "1900-01-01"),
            password=password,
            **extra_fields
        )

    def get_user_by_email_or_phone(self, email: str, phone_number: str):
        return self.filter(
            email_or_phone_condition(email=email, phone_number=phone_number)
        ).first()
