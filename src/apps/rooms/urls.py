# 20241023 수정
from django.urls import path

from apps.amenities.views import amenities_views
from apps.rooms.views import room_views as views

app_name = "rooms"

urlpatterns = [
    # 기본 Room CRUD
    path("", views.RoomListCreateView.as_view(), name="room-list-create"),
    path("<int:pk>/", views.RoomRetrieveUpdateDestroyView.as_view(), name="room-detail"),
    # Room 컴포넌트별 관리
    path("<int:room_id>/type/", views.RoomTypeView.as_view(), name="room-type"),
    path("<int:room_id>/images/", views.RoomImageView.as_view(), name="room-images"),
    path("<int:room_id>/inventory/", views.RoomInventoryView.as_view(), name="room-inventory"),
    path("<int:room_id>/options/", amenities_views.RoomOptionView.as_view(), name="room-option"),
]
