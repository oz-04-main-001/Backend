from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer[User]):  # type: ignore
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

        existing_user: User | None = User.objects.get_user_by_email_or_phone(email=email, phone_number=phone_number)  # type: ignore

        if existing_user:
            if existing_user.email == email:
                raise serializers.ValidationError({"email": "This email is already registered."})
            if existing_user.phone_number == phone_number:
                raise serializers.ValidationError({"phone_number": "This phone number is already registered."})

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Must include both email and password.")

        data["user"] = user
        return data


class UserEmailLookupSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    full_name = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, label="New Password", style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, label="Confirm New Password", style={"input_type": "password"})

    def validate(self, data: dict) -> dict:
        password1 = data.get("password1")
        password2 = data.get("password2")

        if password1 != password2:
            raise serializers.ValidationError("The two password fields didn’t match.")

        return data
