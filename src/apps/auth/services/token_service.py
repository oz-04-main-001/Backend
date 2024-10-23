from typing import Optional

import jwt
from django.conf import settings
from jwt import decode
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken

from apps.common.util.redis_client import get_redis_client
from apps.users.models import User

# Redis 설정
redis_client = get_redis_client()


class TokenService:

    def generate_tokens(self, user: "User") -> str:  # type: ignore

        refresh: RefreshToken = RefreshToken.for_user(user)  # type: ignore
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        self._store_refresh_token_in_redis(user.id, refresh_token, refresh.lifetime)

        return access_token

    @staticmethod
    def _store_refresh_token_in_redis(user_id: int, refresh_token: str, expiration) -> None:
        redis_client.set(f"refresh_{user_id}", refresh_token, ex=expiration)

    @staticmethod
    def _get_stored_refresh_token(user_id: int) -> str:
        stored_refresh_token = redis_client.get(f"refresh_{user_id}")
        if stored_refresh_token is None:
            raise AuthenticationFailed("Refresh token is invalid or has expired.")

        return stored_refresh_token.decode()

    def refresh_access_token(self, access_token: str) -> str:
        try:

            token = AccessToken(str(access_token), verify=False)  # type: ignore

            user_id = token["user_id"]
        except Exception as e:
            raise AuthenticationFailed(f"Invalid access token. {e}")

        stored_refresh_token = self._get_stored_refresh_token(user_id)

        refresh: RefreshToken = RefreshToken(stored_refresh_token)  # type: ignore
        new_access_token = str(refresh.access_token)

        return new_access_token

    @staticmethod
    def delete_refresh_token(user_id: int) -> None:
        redis_client.delete(f"refresh_{user_id}")
        print("삭제 완료")

    @staticmethod
    def validate_access_token(access_token: Optional[str]) -> None:
        if not access_token:
            raise ValidationError("Access token is required.")
