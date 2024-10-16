from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

# 1. 관리자 URL
admin_urlpatterns = [
    path("admin/", admin.site.urls),
]

# 2. 인증 관련 URL (JWT)
auth_urlpatterns = [
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

# 3. API 문서화 (DRF Spectacular)
api_docs_urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# 4. 앱 별 URL (예시로 yourapp과 accounts)
# v1 API 경로
v1_urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("rooms/", include("apps.rooms.urls")),
    path("accommodations/", include("apps.accommodations.urls")),
    path("bookings/", include("apps.bookings.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("amenities/", include("apps.amenities.urls")),
    path("bookmarks/", include("apps.bookmarks.urls")),
    path("host/", include("apps.host_management.urls")),
    path("auth/", include("apps.auth.urls")),
]

# 5. WebSocket 관련 URL
# websocket_urlpatterns = [
#     path("ws/", include("yourapp.routing.websocket_urlpatterns")),
# ]

# 6. 디버그 및 정적 파일 URL (개발 환경에서만)
debug_urlpatterns = []
if settings.DEBUG:
    import debug_toolbar

    debug_urlpatterns = (
        [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )


urlpatterns = (
    debug_urlpatterns
    + admin_urlpatterns
    + auth_urlpatterns
    + api_docs_urlpatterns
    + [path("api/v1/", include(v1_urlpatterns))]  # v1 API 엔드포인트 추가
    # + websocket_urlpatterns
)
