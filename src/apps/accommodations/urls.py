from django.urls import path

from apps.accommodations.views import accommodation_views as views

app_name = "accommodations"

urlpatterns = [
    # 숙소 기본 CRUD
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
    path(
        "search/",
        views.AccommodationSearchView.as_view(),
        name="accommodation-search",
    ),  # GET: /accommodations/search/?search=keyword&min_rating=4&type=hotel
    path(
        "location/<str:city>/<str:state>/",
        views.AccommodationsByLocationView.as_view(),
        name="accommodation-by-location",
    ),  # GET: /accommodations/location/seoul/korea/
    # 숙소 벌크 생성
    path(
        "bulk-create/",
        views.AccommodationBulkCreateView.as_view(),
        name="accommodation-bulk-create",
    ),  # POST: /accommodations/bulk-create/
    # 숙소 타입 관련
    path(
        "types/",
        views.AccommodationTypeListCreateView.as_view(),
        name="accommodation-type-list-create",
    ),  # GET, POST: /accommodations/types/
    path(
        "types/<int:pk>/",
        views.AccommodationTypeRetrieveUpdateDestroyView.as_view(),
        name="accommodation-type-detail",
    ),  # GET, PUT, PATCH, DELETE: /accommodations/types/1/
    path(
        "types/custom/",
        views.AccommodationTypeCustomCreateView.as_view(),
        name="accommodation-type-custom-create",
    ),  # POST: /accommodations/types/custom/
    path(
        "types/statistics/",
        views.AccommodationTypeStatisticsView.as_view(),
        name="accommodation-type-statistics",
    ),  # GET: /accommodations/types/statistics/
    # 이미지 관련
    path(
        "images/",
        views.AccommodationImageListCreateView.as_view(),
        name="accommodation-image-list-create",
    ),  # GET, POST: /accommodations/images/
    path(
        "images/<int:pk>/",
        views.AccommodationImageRetrieveUpdateDestroyView.as_view(),
        name="accommodation-image-detail",
    ),  # GET, PUT, PATCH, DELETE: /accommodations/images/1/
    path(
        "<int:accommodation_id>/images/bulk-upload/",
        views.AccommodationImageBulkUploadView.as_view(),
        name="accommodation-image-bulk-upload",
    ),  # POST: /accommodations/1/images/bulk-upload/
    # GPS 정보
    path(
        "<int:accommodation_id>/gps-info/",
        views.GPSInfoRetrieveUpdateView.as_view(),
        name="gps-info-detail",
    ),  # GET, PUT, PATCH: /accommodations/1/gps-info/
]
