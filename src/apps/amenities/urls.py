from django.urls import path

from .views import ameniites_views as views

app_name = "amenities"

urlpatterns = [
    path("amenities/", views.AmenityListCreateView.as_view(), name="amenity-list-create"),
    path(
        "accommodations/<int:accommodation_id>/amenities/",
        views.AccommodationAmenityListCreateView.as_view(),
        name="accommodation-amenity-list-create",
    ),
    path(
        "accommodations/<int:accommodation_id>/list/",
        views.DetailedAccommodationAmenityListView.as_view(),
        name="accommodation-amenity-list",
    ),
    path("options/", views.OptionListCreateView.as_view(), name="option-list-create"),
    path("rooms/<int:room_id>/options/", views.RoomOptionListCreateView.as_view(), name="room-option-list-create"),
    path("rooms/<int:room_id>/list/", views.DetailedRoomOptionListView.as_view(), name="room-option-list-create"),
    path("custom-amenities/", views.CustomAmenityListView.as_view(), name="custom-amenity-list"),
    path("custom-options/", views.CustomOptionListView.as_view(), name="custom-option-list"),
]
