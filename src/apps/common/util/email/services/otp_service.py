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
    def save_user_data(user_data: dict) -> None:
        redis_client.hmset(f"user:{user_data['email']}", user_data)

    def get_user_data(self, email: str) -> dict:
        data = redis_client.hgetall(f"user:{email}")
        return self._decode_redis_data(data)

    @staticmethod
    def save_data(key: str, value: str, ttl: int = 600) -> None:
        redis_client.set(key, value, ex=ttl)

    @staticmethod
    def get_data(key: str) -> str:
        data = redis_client.get(key)
        return data.decode("utf-8") if data else None

    @staticmethod
    def delete_data(key: str) -> None:
        redis_client.delete(key)

    @staticmethod
    def _decode_redis_data(data: dict):
        return {key.decode("utf-8"): value.decode("utf-8") for key, value in data.items()}

    @staticmethod
    def delete_user_data(email: str) -> None:
        redis_client.delete(f"user:{email}")

    @staticmethod
    def delete_otp_from_redis(email: str) -> None:
        redis_client.delete(f"otp:{email}")

    def send_otp_email(self, to_email: str) -> str:
        otp = self._generate_otp()
        self._save_otp_to_redis(to_email, otp)

        subject = "Your OTP Code"
        message = f"Your OTP code is {otp}. It will expire in 10 minutes."
        email = to_email if isinstance(to_email, list) else [to_email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, email)
        return otp
