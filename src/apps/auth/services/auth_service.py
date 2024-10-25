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
    def find_user_by_phone(phone_number: str) -> User | None:
        return User.objects.get_user_by_phone(phone_number)

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
        user.is_active = False
        user.save()

    @staticmethod
    def check_if_email_exists(email: str) -> bool:
        return User.objects.filter(email=email).exists()
