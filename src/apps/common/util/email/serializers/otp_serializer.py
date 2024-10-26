from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.common.util.email.services.otp_service import OTPService


class BaseOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

    def validate_otp(self, value):
        if len(value) != 6:
            raise serializers.ValidationError("OTP must be 6 digits.")
        return value

    def validate(self, data: dict) -> dict:
        raise NotImplementedError("Subclasses must implement validate method.")


class RegistrationOTPVerificationSerializer(BaseOTPSerializer):
    email = serializers.EmailField(required=False)

    def validate(self, data: dict) -> dict:
        user_data = self.context.get("user_data")
        email = data.get("email")
        otp = data.get("otp")

        stored_otp = OTPService.get_otp_from_redis(email)

        if not email:
            raise serializers.ValidationError("No email found.")
        if not user_data:
            raise serializers.ValidationError("User data not found in session.")
        if not stored_otp or stored_otp.decode() != otp:
            raise ValidationError("Invalid or expired OTP.")

        data["user_data"] = user_data

        return data


class UserOTPVerificationSerializer(BaseOTPSerializer):
    def validate(self, data: dict) -> dict:
        email = self.context.get("email")
        otp = data.get("otp")

        stored_otp = OTPService.get_otp_from_redis(email)

        if not email:
            raise ValidationError("No email found.")
        if not stored_otp or stored_otp.decode() != otp:
            raise ValidationError("Invalid or expired OTP.")

        data["email"] = email

        return data
