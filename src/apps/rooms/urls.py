from django.urls import path

from .views import room_views as views

app_name = "rooms"

urlpatterns = [
    path("", views.RoomListCreateView.as_view(), name="room-list-create"),
    path('accommodation/<int:accommodation_id>/', views.AccommodationRoomsView.as_view(), name='accommodation-rooms'),
    path("<int:pk>/", views.RoomDetailView.as_view(), name="room-detail"),
    path("<int:pk>/add-image/", views.RoomImageCreateView.as_view(), name="room-add-image"),
    path("types/", views.RoomTypeListCreateView.as_view(), name="room-type-list-create"),
    path("types/custom/", views.RoomTypeCustomCreateView.as_view(), name="room-type-custom-create"),
    path("inventory/<int:pk>/", views.RoomInventoryUpdateView.as_view(), name="room-inventory-update"),
]
