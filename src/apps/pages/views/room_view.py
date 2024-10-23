from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.pages.serializers.room_serializer import RoomSerializer
from apps.rooms.models import Room


@extend_schema(tags=["Guest"])
class RoomDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
