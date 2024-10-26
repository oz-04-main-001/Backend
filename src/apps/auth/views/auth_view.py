from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.auth.serializers.auth_serializer import (
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserEmailLookupSerializer,
    UserOTPRequestSerializer,
    UserRegistrationSerializer,
)
from apps.auth.serializers.token_serializer import TokenSerializer
from apps.auth.services.auth_service import UserAuthService
from apps.auth.services.token_service import TokenService
from apps.common.util.email.serializers.otp_serializer import (
    RegistrationOTPVerificationSerializer,
    UserOTPVerificationSerializer,
)
from apps.common.util.email.services.otp_service import OTPService
from apps.users.models import User, WithdrawManager  # type: ignore


@extend_schema(tags=["User"])
class UserRegistrationRequestAPIView(GenericAPIView):  # type: ignore
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    otp_service = OTPService()

    @extend_schema(
        summary="사용자 회원가입 API",
        request=UserRegistrationSerializer,
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        해당 API로 회원가입 요청을 보내세요. 요청을 보낼 시 user_data는 session에 저장되어 있어 프론트에서 관리 하지 않아도 됩니다 \n\n
        날짜:  YYYY - MM - DD 형식 \n\n
        전화번호:  010-1234-5678 형식
        """
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
    serializer_class = RegistrationOTPVerificationSerializer

    otp_service = OTPService()
    user_auth_service = UserAuthService()

    @extend_schema(
        request=RegistrationOTPVerificationSerializer,
        summary="회원가입 OTP 검증 API",
        description="해당 API는 OTP 검증을 위한 api입니다.",
    )
    def post(self, request, *args, **kwargs):
        user_data = request.session.get("user_data")

        serializer = self.get_serializer(data=request.data, context={"user_data": user_data})
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        email = validated_data.get("email")
        user_validated_data = validated_data.get("user_data")

        self.otp_service.delete_otp(email)

        self.user_auth_service.create_user(validated_data=user_validated_data)

        del request.session["user_data"]

        return Response(
            {"message": "OTP verified and user created successfully."},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["User"])
class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    token_service = TokenService()

    @extend_schema(
        request=LoginSerializer,
        summary="사용자 로그인 API",
        description="이메일과 비밀번호를 입력하고 로그인하는 API입니다",
    )
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
class CustomTokenRefreshView(GenericAPIView):
    serializer_class = TokenSerializer
    permission_classes = [AllowAny]
    token_service = TokenService()

    @extend_schema(
        request=TokenSerializer,
        summary="Access token 재발급 API",
        description="Access Token을 재발급합니다. \n\n 만약 Refresh token도 만료 시 401 에러 -> 로그인 페이지",
    )
    def post(self, request, *args, **kwargs):

        access_token_raw = request.auth

        serializer = self.get_serializer(data=request.data, context={"access_token": access_token_raw})
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data.get("access_token")

        try:
            new_access_token = self.token_service.refresh_access_token(access_token=access_token)

            return Response(
                {
                    "access_token": new_access_token,
                },
                status=status.HTTP_200_OK,
            )
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["User"])
class LogoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    token_service = TokenService()

    @extend_schema(
        summary="사용자 로그아웃 API",
    )
    def post(self, request, *args, **kwargs):
        """
        사용자 로그아웃 API입니다. 가지고 있던 Refresh token을 만료시킵니다. \n\n
        Access token은 만료되지 않습니다. 대신 access token의 주기를 짧게 가져가고 \n\n
        Refresh token의 주기는 길게 가져갑니다.
        """
        user = request.user

        self.token_service.delete_refresh_token(user.id)

        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class UserDeletionRequestAPIView(GenericAPIView):
    serializer_class = UserOTPRequestSerializer
    permission_classes = [IsAuthenticated]
    otp_service = OTPService()

    @extend_schema(
        request=UserOTPRequestSerializer,
        summary="사용자 삭제 요청 API",
        description="사용자가 회원가입 시 등록했던 이메일로 otp 이메일 발송",
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        withdraw_reason = request.data.get("withdraw_reason", "")  # 당장은 없기에 시리얼 라이저 x
        user = request.user

        serializer = self.get_serializer(data=request.data, context={"email": user.email})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        self.otp_service.send_otp_email(email)  # type: ignore

        request.session["withdraw_reason"] = withdraw_reason

        return Response(
            {"message": "OTP has been sent to your email. Please verify."},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["User"])
class UserDeletionVerifyAPIView(GenericAPIView):
    serializer_class = UserOTPVerificationSerializer
    permission_classes = [IsAuthenticated]
    user_auth_service = UserAuthService()

    @extend_schema(
        request=UserOTPVerificationSerializer,
        summary="사용자 삭제 OTP 검증",
        description="해당 API는 OTP 검증 후 사용자를 비활성화합니다",
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        email = user.email

        serializer = self.get_serializer(data=request.data, context={"email": email})
        serializer.is_valid(raise_exception=True)

        withdraw_reason = request.session.get("withdraw_reason", "")  # 이후 검증 로직 추가

        self.user_auth_service.create_withdraw_record(withdraw_reason=withdraw_reason, user=user)

        del request.session["withdraw_reason"]

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["User"])
class UserEmailLookupAPIView(GenericAPIView):
    serializer_class = UserEmailLookupSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()

    @extend_schema(
        request=UserEmailLookupSerializer,
        summary="사용자 이메일 조회 API",
    )
    def post(self, request, *args, **kwargs):
        """
        사용자의 이름과 전화번호를 바탕으로 이메일을 조회합니다 \n\n
        전화 번호:  010-1234-5678 형식
        """
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

    @extend_schema(
        request=PasswordResetRequestSerializer,
        summary="비밀번호 재설정 요청 API",
        description="비밀번호 재설정 요청 API입니다. 입력한 이메일로 검증 메일 발송",
    )
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
    serializer_class = UserOTPVerificationSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()
    otp_service = OTPService()

    @extend_schema(
        request=UserOTPVerificationSerializer,
        summary="비밀번호 검증 API",
        description="해당 API는 OTP 검증 후 비밀번호 재설정 api로 이동",
    )
    def post(self, request, *args, **kwargs):

        email = request.session.get("reset_email")
        serializer = self.get_serializer(data=request.data, context={"email": email})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        self.otp_service.delete_otp(email)

        request.session["otp_verified"] = True

        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()
    otp_service = OTPService()

    @extend_schema(
        request=PasswordResetSerializer,
        summary="비밀번호 재설정 API",
        description="해당 API는 OTP 검증이 끝난 사용자만 접근 가능합니다. 새로운 비밀번호를 설정해주세요",
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        email = request.session.get("reset_email")
        otp_verified = request.session.get("otp_verified", False)

        serializer = self.get_serializer(
            data=request.data,
            context={
                "email": email,
                "otp_verified": otp_verified,
            },
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user")
        password = serializer.validated_data.get("password")

        self.user_auth_service.set_user_password(user, password)

        del request.session["reset_email"]
        del request.session["otp_verified"]

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


# 비밀번호 변경 후 로그인 에러 처리
