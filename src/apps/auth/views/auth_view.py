import datetime
from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.auth.serializers.auth_serializer import (
    AccessTokenResponseSerializer,
    AuthResponseSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserEmailLookupResponseSerializer,
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
from apps.users.models import BusinessUser, User, WithdrawManager  # type: ignore


@extend_schema(tags=["User"])
class UserRegistrationRequestAPIView(GenericAPIView):  # type: ignore
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    otp_service = OTPService()

    @extend_schema(
        summary="사용자 회원가입 API",
        request=UserRegistrationSerializer,
        responses={
            200: AuthResponseSerializer,
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        해당 API로 회원가입 요청을 보내세요. 요청을 보낼 시 user_data는 session에 저장되어 있어 프론트에서 관리 하지 않아도 됩니다 \n\n
        날짜:  YYYY - MM - DD 형식 \n\n
        전화번호:  010-1234-5678 형식
        """
        serializer = self.get_serializer(data=request.data, context={"ip_address": request.META.get("REMOTE_ADDR")})
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        email = validated_data.get("email")
        self.otp_service.send_otp_email(email)

        birth_date = validated_data.get("birth_date")
        if isinstance(birth_date, datetime.date):
            birth_date = birth_date.strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식으로 변환

        validated_data["birth_date"] = birth_date

        self.otp_service.save_user_data(validated_data)

        response_serializer = AuthResponseSerializer({"message": "OTP has been sent to your email. Please verify."})

        return Response(
            response_serializer.data,
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
        responses={
            200: AuthResponseSerializer,
        },
        summary="회원가입 OTP 검증 API",
        description="해당 API는 OTP 검증을 위한 api입니다.",
    )
    def post(self, request, *args, **kwargs):
        user_data = self.otp_service.get_user_data(request.data.get("email"))

        serializer = self.get_serializer(data=request.data, context={"user_data": user_data})
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        email = validated_data.get("email")
        user_validated_data = validated_data.get("user_data")

        self.otp_service.delete_otp_from_redis(email=email)
        self.otp_service.delete_user_data(email=email)

        self.user_auth_service.create_user(validated_data=user_validated_data)

        response_serializer = AuthResponseSerializer({"message": "OTP verified and user created successfully."})

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["User"])
class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    token_service = TokenService()

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
        },
        summary="사용자 로그인 API",
        description="이메일과 비밀번호를 입력하고 로그인하는 API입니다",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        access_token = self.token_service.generate_tokens(user=user)

        response_data = {
            "access_token": access_token,
            "user_type": user.user_type,
            "name": user.name,
            "phone_number": user.phone_number,
        }

        response_serializer = LoginResponseSerializer(response_data)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["User"])
class CustomTokenRefreshView(GenericAPIView):
    authentication_classes = []
    serializer_class = TokenSerializer
    permission_classes = [AllowAny]
    token_service = TokenService()

    @extend_schema(
        request=TokenSerializer,
        responses={
            200: AccessTokenResponseSerializer,
        },
        summary="Access token 재발급 API",
        description="Access Token을 재발급합니다. \n\n 만약 Refresh token도 만료 시 401 에러 -> 로그인 페이지",
    )
    def post(self, request, *args, **kwargs):
        authorization = request.headers.get("Authorization")
        access_token_raw = authorization.split(" ")[1] if authorization else None

        serializer = self.get_serializer(data=request.data, context={"access_token": access_token_raw})
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data.get("access_token")

        try:
            new_access_token = self.token_service.refresh_access_token(access_token=access_token)
            response_serializer = AccessTokenResponseSerializer({"access_token": new_access_token})
            return Response(
                response_serializer.data,
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
        responses={
            200: AuthResponseSerializer,
        },
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

        response_serializer = AuthResponseSerializer({"message": "Successfully logged out."})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class UserDeletionRequestAPIView(GenericAPIView):
    serializer_class = UserOTPRequestSerializer
    permission_classes = [IsAuthenticated]
    otp_service = OTPService()

    @extend_schema(
        request=UserOTPRequestSerializer,
        responses={
            200: AuthResponseSerializer,
        },
        summary="사용자 삭제 요청 API",
        description="사용자가 회원가입 시 등록했던 이메일로 otp 이메일 발송",
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        withdraw_reason = request.data.get("withdraw_reason", "")  # 당장은 없기에 시리얼 라이저 x
        user = request.user
        ip_address = request.META.get("REMOTE_ADDR")

        serializer = self.get_serializer(
            data=request.data,
            context={
                "email": user.email,
                "ip_address": ip_address,
            },
        )

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        self.otp_service.send_otp_email(email)  # type: ignore

        request.session["withdraw_reason"] = withdraw_reason

        response_serializer = AuthResponseSerializer({"message": "OTP has been sent to your email. Please verify."})
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["User"])
class UserDeletionVerifyAPIView(GenericAPIView):
    serializer_class = UserOTPVerificationSerializer
    permission_classes = [IsAuthenticated]
    user_auth_service = UserAuthService()

    @extend_schema(
        request=UserOTPVerificationSerializer,
        responses={
            200: AuthResponseSerializer,
        },
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

        response_serializer = AuthResponseSerializer({"message": "User deleted successfully."})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class UserEmailLookupAPIView(GenericAPIView):
    serializer_class = UserEmailLookupSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()

    @extend_schema(
        request=UserEmailLookupSerializer,
        responses={
            200: UserEmailLookupResponseSerializer,
        },
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

        response_serializer = UserEmailLookupResponseSerializer({"email": user.email})

        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class PasswordResetRequestAPIView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    otp_service = OTPService()
    user_auth_service = UserAuthService()

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: AuthResponseSerializer,
        },
        summary="비밀번호 재설정 요청 API",
        description="비밀번호 재설정 요청 API입니다. 입력한 이메일로 검증 메일 발송",
    )
    def post(self, request, *args, **kwargs):
        ip_address = request.META.get("REMOTE_ADDR")

        serializer = self.get_serializer(data=request.data, context={"ip_address": ip_address})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        otp = self.otp_service.send_otp_email(email)
        self.otp_service.save_data(f"email:{otp}", email)

        response_serializer = AuthResponseSerializer({"message": "OTP has been sent to your email."})
        return Response(
            response_serializer.data,
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
        responses={
            200: AuthResponseSerializer,
        },
        summary="비밀번호 검증 API",
        description="해당 API는 OTP 검증 후 비밀번호 재설정 api로 이동",
    )
    def post(self, request, *args, **kwargs):

        otp = request.data.get("otp")
        email = self.otp_service.get_data(key=f"email:{otp}")
        serializer = self.get_serializer(data=request.data, context={"email": email})
        serializer.is_valid(raise_exception=True)

        self.otp_service.delete_otp_from_redis(email)

        response_serializer = AuthResponseSerializer({"message": "OTP verified successfully."})
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    user_auth_service = UserAuthService()
    otp_service = OTPService()

    @extend_schema(
        request=PasswordResetSerializer,
        responses={
            200: AuthResponseSerializer,
        },
        summary="비밀번호 재설정 API",
        description="해당 API는 OTP 검증이 끝난 사용자만 접근 가능합니다. 새로운 비밀번호를 설정해주세요",
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:

        otp = request.data.get("otp")
        email = self.otp_service.get_data(f"email:{otp}")

        serializer = self.get_serializer(
            data=request.data,
            context={
                "email": email,
            },
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user")
        password = serializer.validated_data.get("password")

        self.user_auth_service.set_user_password(user, password)

        self.otp_service.delete_data(f"email:{otp}")

        response_serializer = AuthResponseSerializer({"message": "Password has been reset successfully."})
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
