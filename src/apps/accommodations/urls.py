# 20241024 수정
from django.urls import path

from apps.accommodations.views import accommodation_views as views
from apps.amenities.views import amenities_views

app_name = "accommodations"
urlpatterns = [
    # 숙소 기본 CRUD (accommodation, amenities, type, image, gps create)
    path(
        "",
        views.AccommodationListCreateView.as_view(),
        name="accommodation-list-create",
    ),  # GET, POST: /accommodations/
    path(
        "<int:pk>/",
        views.AccommodationRetrieveUpdateDestroyView.as_view(),
        name="accommodation-detail",
    ),  # GET, PUT, PATCH, DELETE: /accommodations/1/
    # 숙소 검색
    # 이미지 관련
    path(
        "images/<int:pk>/",
        views.AccommodationImageView.as_view(),
        name="accommodation-image-detail",
    ),  # GET, PUT, PATCH, DELETE: /accommodations/images/1/
    # GPS 정보
    path(
        "<int:accommodation_id>/gps-info/",
        views.GPSInfoView.as_view(),
        name="gps-info-detail",
    ),  # GET, PUT, PATCH: /accommodations/1/gps-info/
    # amenity 정보
    path(
        "<int:accommodation_id>/amenities/",
        amenities_views.AccommodationAmenityView.as_view(),
        name="accommodation-amenities",
    ),
]
