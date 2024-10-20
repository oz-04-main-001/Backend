from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

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
    def _store_refresh_token_in_redis(user_id: int, refresh_token: str, expiration):
        redis_client.set(f"refresh_token:{user_id}", refresh_token, ex=expiration)

    @staticmethod
    def _get_stored_refresh_token(user_id: int) -> str:
        stored_refresh_token = redis_client.get(f"refresh_token:{user_id}")
        if stored_refresh_token is None:
            raise AuthenticationFailed("Refresh token is invalid or has expired.")

        return stored_refresh_token.decode()

    def refresh_access_token(self, access_token: str):
        try:
            token: AccessToken = AccessToken(access_token)  # type: ignore
            user_id = token["user_id"]
        except Exception:
            raise AuthenticationFailed("Invalid access token.")

        stored_refresh_token = self._get_stored_refresh_token(user_id)

        refresh: RefreshToken = RefreshToken(stored_refresh_token)  # type: ignore
        new_access_token = str(refresh.access_token)

        return new_access_token

    @staticmethod
    def delete_refresh_token(user_id: int) -> None:
        redis_client.delete(f"refresh_token:{user_id}")
