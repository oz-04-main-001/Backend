import random
import string

from django.conf import settings
from django.core.mail import send_mail

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

    def verify_otp(self, email: str, otp: str) -> bool:
        stored_otp = self.get_otp_from_redis(email)
        if stored_otp and stored_otp.decode() == otp:
            self.delete_otp_from_redis(email)
            return True
        return False
