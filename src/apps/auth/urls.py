from django.urls import path

from . import views
from .views.auth_view import (
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
]
