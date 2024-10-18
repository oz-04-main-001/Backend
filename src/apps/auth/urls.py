from django.urls import path

from .views.auth_view import (
    CustomTokenRefreshView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetAPIView,
    PasswordResetRequestAPIView,
    PasswordResetVerifyAPIView,
    UserDeletionRequestAPIView,
    UserDeletionVerifyAPIView,
    UserEmailLookupAPIView,
    UserRegistrationRequestAPIView,
    UserRegistrationVerifyAPIView,
)

app_name = "auth"  # 앱 이름 설정

urlpatterns = [
    path(
        "register/request/",
        UserRegistrationRequestAPIView.as_view(),
        name="user-register-request",
    ),
    path(
        "register/verify/",
        UserRegistrationVerifyAPIView.as_view(),
        name="user-register-verify",
    ),
    path("login/", LoginAPIView.as_view(), name="login"),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path(
        "delete/request/",
        UserDeletionRequestAPIView.as_view(),
        name="user-delete_request",
    ),
    path(
        "delete/verify/",
        UserDeletionVerifyAPIView.as_view(),
        name="user-delete_verify",
    ),
    path(
        "email-lookup/",
        UserEmailLookupAPIView.as_view(),
        name="password-email_lookup",
    ),
    path(
        "password/reset/request/",
        PasswordResetRequestAPIView.as_view(),
        name="password-reset_request",
    ),
    path(
        "password/reset/verify/",
        PasswordResetVerifyAPIView.as_view(),
        name="password-reset_verify",
    ),
    path(
        "password/reset/",
        PasswordResetAPIView.as_view(),
        name="password-reset",
    ),
]
