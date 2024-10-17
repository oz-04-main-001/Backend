from rest_framework import serializers

from apps.users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer[User]):
    password2 = serializers.CharField(write_only=True, label="Confirm Password")

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "birth_date",
            "gender",
            "phone_number",
        ]

    def validate(self, data: dict) -> dict:
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})

        email = data.get("email")
        phone_number = data.get("phone_number")

        existing_user = User.objects.get_user_by_email_or_phone(
            email=email, phone_number=phone_number
        )

        if existing_user:
            if existing_user.email == email:
                raise serializers.ValidationError(
                    {"email": "This email is already registered."}
                )
            if existing_user.phone_number == phone_number:
                raise serializers.ValidationError(
                    {"phone_number": "This phone number is already registered."}
                )

        return data
