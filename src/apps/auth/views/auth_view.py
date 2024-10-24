from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth.serializers.auth_serializer import (
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserEmailLookupSerializer,
    UserRegistrationSerializer,
)
from apps.auth.services.auth_service import UserAuthService
from apps.auth.services.token_service import TokenService
from apps.common.util.email.serializers.otp_serializer import OTPVerificationSerializer
from apps.common.util.email.services.otp_service import OTPService
from apps.users.models import User, WithdrawManager  # type: ignore


@extend_schema(tags=["User"])
class UserRegistrationRequestAPIView(GenericAPIView):  # type: ignore
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    otp_service = OTPService()

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        email = validated_data.get("email")
        self.otp_service.send_otp_email(email)

        request.session["user_data"] = validated_data

        return Response(
            {"message": "OTP has been sent to your email. Please verify."},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["User"])
class UserRegistrationVerifyAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    otp_service = OTPService()
    user_auth_service = UserAuthService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        email = validated_data.get("email")
        otp = validated_data.get("otp")
        user_data = request.session.get("user_data")

        try:
            self.otp_service.verify_otp(email, otp)

            self.user_auth_service.validate_user_data_in_session(user_data)

            self.user_auth_service.create_user(validated_data=user_data)

            del request.session["user_data"]

            return Response(
                {"message": "OTP verified and user created successfully."},
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["User"])
class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    token_service = TokenService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        access_token = self.token_service.generate_tokens(user=user)

        return Response(
            {
                "access_token": access_token,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["User"])
class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    token_service = TokenService()

    def post(self, request, *args, **kwargs):
        try:
            access_token = request.auth

            self.token_service.validate_access_token(access_token)

            new_access_token = self.token_service.refresh_access_token(access_token=access_token)

            return Response(
                {
                    "access_token": new_access_token,
                },
                status=status.HTTP_200_OK,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred." + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=["User"])
class LogoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    token_service = TokenService()

    def post(self, request, *args, **kwargs):
        user = request.user

        self.token_service.delete_refresh_token(user.id)

        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class UserDeletionRequestAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    otp_service = OTPService()

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        withdraw_reason = request.data.get("withdraw_reason", "")  # 당장은 없기에 시리얼 라이저 x

        user = request.user

        self.otp_service.send_otp_email(user.email)  # type: ignore

        request.session["withdraw_reason"] = withdraw_reason

        return Response(
            {"message": "OTP has been sent to your email. Please verify."},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["User"])
class UserDeletionVerifyAPIView(GenericAPIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = [IsAuthenticated]
    user_auth_service = UserAuthService()

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdraw_reason = request.session.get("withdraw_reason", "")  # 이후 검증 로직 추가

        user = request.user

        self.user_auth_service.create_withdraw_record(withdraw_reason=withdraw_reason, user=user)

        del request.session["withdraw_reason"]

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["User"])
class UserEmailLookupAPIView(GenericAPIView):
    serializer_class = UserEmailLookupSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        return Response({"email": user.email}, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class PasswordResetRequestAPIView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    otp_service = OTPService()
    user_auth_service = UserAuthService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        request.session["reset_email"] = email

        self.otp_service.send_otp_email(email)

        return Response(
            {"message": "OTP has been sent to your email."},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["User"])
class PasswordResetVerifyAPIView(GenericAPIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()
    otp_service = OTPService()

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = request.session.get("reset_email")
            self.user_auth_service.validate_email_in_session(email=email)
            otp = serializer.validated_data.get("otp")

            self.otp_service.verify_otp(email, otp)

            request.session["otp_verified"] = True

            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["User"])
class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()
    otp_service = OTPService()

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            email = request.session.get("reset_email")
            otp_verified = request.session.get("otp_verified", False)

            self.user_auth_service.validate_email_in_session(email=email)
            self.otp_service.validate_otp_verified_in_session(otp_verified=otp_verified)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            password = serializer.validated_data.get("password")

            user: User | None = self.user_auth_service.get_user_by_email(email=email)
            self.user_auth_service.set_user_password(user, password)

            del request.session["reset_email"]
            del request.session["otp_verified"]

            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )

        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
