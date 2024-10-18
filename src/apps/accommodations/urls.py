from django.urls import path

from .views import accommodation_views as views

app_name = "accommodations"

urlpatterns = [
    path(
        "",
        views.AccommodationListCreateView.as_view(),
        name="accommodation-list-create",
    ),
    path(
        "<int:pk>/",
        views.AccommodationRetrieveUpdateDestroyView.as_view(),
        name="accommodation-detail",
    ),
    path(
        "types/",
        views.AccommodationTypeListCreateView.as_view(),
        name="accommodation-type-list-create",
    ),
    path(
        "types/<int:pk>/",
        views.AccommodationTypeRetrieveUpdateDestroyView.as_view(),
        name="accommodation-type-detail",
    ),
    path(
        "types/custom/",
        views.AccommodationTypeCustomCreateView.as_view(),
        name="accommodation-type-custom-create",
    ),
    path(
        "images/",
        views.AccommodationImageListCreateView.as_view(),
        name="accommodation-image-list-create",
    ),
    path(
        "images/<int:pk>/",
        views.AccommodationImageRetrieveUpdateDestroyView.as_view(),
        name="accommodation-image-detail",
    ),
    path(
        "<int:accommodation_id>/gps-info/",
        views.GPSInfoRetrieveUpdateView.as_view(),
        name="gps-info-detail",
    ),
]
