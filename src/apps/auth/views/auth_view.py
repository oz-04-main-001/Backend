from typing import Any

from rest_framework import status
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
from apps.auth.services.token_service import TokenService
from apps.common.util.email.serializers.otp_serializer import OTPVerificationSerializer
from apps.common.util.email.services.otp_service import OTPService
from apps.users.models import User, WithdrawManager  # type: ignore


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


class UserRegistrationVerifyAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    otp_service = OTPService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        email = validated_data.get("email")
        otp = validated_data.get("otp")

        if self.otp_service.verify_otp(email, otp):
            user_data = request.session.get("user_data")

            if not user_data:
                return Response(
                    {"message": "User data not found in session."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            User.objects.create_user(
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone_number=user_data["phone_number"],
                gender=user_data["gender"],
                birth_date=user_data["birth_date"],
                password=user_data["password"],
            )

            del request.session["user_data"]

            return Response(
                {"message": "OTP verified and user created successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response({"message": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)


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


class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    token_service = TokenService()

    def post(self, request, *args, **kwargs):
        access_token = request.auth

        if not access_token:
            return Response(
                {"detail": "Access token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_access_token = self.token_service.refresh_access_token(access_token=access_token)

        return Response(
            {
                "access_token": new_access_token,
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    token_service = TokenService()

    def post(self, request, *args, **kwargs):
        user = request.user

        self.token_service.delete_refresh_token(f"refresh_token:{user.id}")

        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserDeletionRequestAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    otp_service = OTPService()

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        withdraw_reason = request.data.get("withdraw_reason", "")

        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "User is not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        self.otp_service.send_otp_email(user.email)  # type: ignore

        request.session["withdraw_reason"] = withdraw_reason

        return Response(
            {"message": "OTP has been sent to your email. Please verify."},
            status=status.HTTP_200_OK,
        )


class UserDeletionVerifyAPIView(GenericAPIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdraw_reason = request.session.get("withdraw_reason", "")

        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "User is not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        WithdrawManager.objects.create(
            user=user,
            withdraw_reason=withdraw_reason,
        )

        del request.session["withdraw_reason"]

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserEmailLookupAPIView(GenericAPIView):
    serializer_class = UserEmailLookupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data.get("phone_number")
        full_name = serializer.validated_data.get("full_name")

        last_name = full_name[0]
        first_name = full_name[1:]

        user = User.objects.get_user_by_phone_and_name(phone_number, first_name, last_name)

        if not user:
            return Response(
                {"error": "No user found with this phone number and full name."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"email": user.email}, status=status.HTTP_200_OK)


class PasswordResetRequestAPIView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    otp_service = OTPService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        if not User.objects.email_exists(email=email):
            return Response(
                {"error": "No user is associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        request.session["reset_email"] = email

        self.otp_service.send_otp_email(email)

        return Response(
            {"message": "OTP has been sent to your email."},
            status=status.HTTP_200_OK,
        )


class PasswordResetVerifyAPIView(GenericAPIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny]
    otp_service = OTPService()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.session.get("reset_email")
        otp = serializer.validated_data.get("otp")

        if not email:
            return Response(
                {"error": "No email found in session."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not self.otp_service.verify_otp(email, otp):
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        request.session["otp_verified"] = True

        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)


class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def patch(self, request: Request, *args, **kwargs) -> Response:

        otp_verified = request.session.get("otp_verified")
        if not otp_verified:
            return Response(
                {"error": "OTP verification required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.session.get("reset_email")
        password = serializer.validated_data.get("password")

        if not email:
            return Response(
                {"error": "No email found in session."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user: User | None = User.objects.get_user_by_email(email=email)
        user.set_password(password)  # type: ignore
        user.save()  # type: ignore

        del request.session["reset_email"]
        del request.session["otp_verified"]

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )
