from typing import Any

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.auth.serializers.auth_serializer import UserRegistrationSerializer
from apps.common.util.email.serializers.otp_serializer import OTPVerificationSerializer
from apps.common.util.email.services.otp_service import OTPService
from apps.users.models import User


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

        return Response(
            {"message": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST
        )
