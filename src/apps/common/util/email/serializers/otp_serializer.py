from rest_framework import serializers


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate_otp(self, value):
        """
        OTP 길이 검증 (기본적으로 6자리)
        """
        if len(value) != 6:
            raise serializers.ValidationError("OTP must be 6 digits.")
        return value
