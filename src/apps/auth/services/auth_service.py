from botocore.exceptions import ValidationError
from rest_framework.exceptions import NotFound

from apps.users.models import User, WithdrawManager


class UserAuthService:
    @staticmethod
    def create_user(validated_data: dict) -> User:
        return User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            gender=validated_data["gender"],
            birth_date=validated_data["birth_date"],
            password=validated_data["password"],
        )

    @staticmethod
    def deactivate_user(user: User) -> None:
        user.is_active = False
        user.save()

    @staticmethod
    def find_user_by_phone_and_name(phone_number: str, first_name: str, last_name: str) -> User | None:
        return User.objects.get_user_by_phone_and_name(phone_number, first_name, last_name)

    @staticmethod
    def get_user_by_email(email: str) -> User:
        user = User.objects.get_user_by_email(email=email)
        if not user:
            raise NotFound("User with this email does not exist.")
        return user

    @staticmethod
    def set_user_password(user: User, password: str) -> None:
        user.set_password(password)
        user.save()

    @staticmethod
    def create_withdraw_record(user: User, withdraw_reason: str) -> None:
        WithdrawManager.objects.create(
            user=user,
            withdraw_reason=withdraw_reason,
        )

    @staticmethod
    def check_if_email_exists(email: str) -> bool:
        return User.objects.filter(email=email).exists()

    @staticmethod
    def validate_email_in_session(email: str) -> None:
        if not email:
            raise ValidationError("No email found.")

    @staticmethod
    def validate_user_data_in_session(user_data: dict) -> None:
        if not user_data:
            raise ValidationError("User data not found in session.")
