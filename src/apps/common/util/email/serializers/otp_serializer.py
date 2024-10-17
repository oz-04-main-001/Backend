from rest_framework import serializers


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    otp = serializers.CharField(max_length=6)

    def validate_otp(self, value):
        if len(value) != 6:
            raise serializers.ValidationError("OTP must be 6 digits.")
        return value
