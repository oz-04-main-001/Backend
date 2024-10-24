# 20241024 수정
from django.urls import path

from apps.amenities.views import amenities_views as views

app_name = "amenities"

urlpatterns = [
    # Base amenity endpoints
    path("custom-amenities/", views.CustomAmenityListView.as_view(), name="custom-amenity-list"),
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
