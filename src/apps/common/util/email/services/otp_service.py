import random
import string

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

from apps.common.util.redis_client import get_redis_client

redis_client = get_redis_client()


class OTPService:
    @staticmethod
    def _generate_otp(length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def _save_otp_to_redis(email: str, otp: str, expiry: int = 600) -> None:
        redis_client.set(f"otp:{email}", otp, ex=expiry)

    @staticmethod
    def get_otp_from_redis(email: str) -> bytes:
        return redis_client.get(f"otp:{email}")

    @staticmethod
    def delete_otp_from_redis(email: str) -> None:
        redis_client.delete(f"otp:{email}")

    def send_otp_email(self, to_email: str) -> None:
        otp = self._generate_otp()
        self._save_otp_to_redis(to_email, otp)

        subject = "Your OTP Code"
        message = f"Your OTP code is {otp}. It will expire in 10 minutes."
        email = to_email if isinstance(to_email, list) else [to_email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, email)

    def verify_otp(self, email: str, otp: str) -> None:
        """OTP의 유효성을 검증하고, 유효하지 않으면 예외 발생"""
        stored_otp = self.get_otp_from_redis(email)
        if not stored_otp or stored_otp.decode() != otp:
            raise ValidationError("Invalid or expired OTP.")
        self.delete_otp_from_redis(email)

    def validate_otp_verified_in_session(self, otp_verified: bool) -> None:
        """OTP 검증 상태 확인"""
        if not otp_verified:
            raise ValidationError("OTP verification required.")
