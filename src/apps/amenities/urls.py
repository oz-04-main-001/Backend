# 20241023 수정
from django.urls import path

from apps.amenities.views import ameniites_views as views

app_name = "amenities"

urlpatterns = [
    # Base amenity endpoints
    path("amenities/", views.AmenityListCreateView.as_view(), name="amenity-list-create"),
    path("amenities/<int:pk>/", views.AmenityDetailView.as_view(), name="amenity-detail"),  # 추가
    path("custom-amenities/", views.CustomAmenityListView.as_view(), name="custom-amenity-list"),
    # Accommodation amenity endpoints
    path(
        "accommodations/<int:accommodation_id>/amenities/",
        views.AccommodationAmenityListCreateView.as_view(),
        name="accommodation-amenity-list-create",
    ),
    path(
        "accommodations/<int:accommodation_id>/amenities/<int:pk>/",  # 추가
        views.AccommodationAmenityDetailView.as_view(),
        name="accommodation-amenity-detail",
    ),
    # Base option endpoints
    path("options/", views.OptionListCreateView.as_view(), name="option-list-create"),
    path("options/<int:pk>/", views.OptionDetailView.as_view(), name="option-detail"),  # 추가
    path("custom-options/", views.CustomOptionListView.as_view(), name="custom-option-list"),
    # Room option endpoints
    path("rooms/<int:room_id>/options/", views.RoomOptionListCreateView.as_view(), name="room-option-list-create"),
    path(
        "rooms/<int:room_id>/options/<int:pk>/",  # 추가
        views.RoomOptionDetailView.as_view(),
        name="room-option-detail",
    ),
]
