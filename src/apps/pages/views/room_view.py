from rest_framework.generics import RetrieveAPIView

from apps.pages.serializers.room_serializer import RoomSerializer
from apps.rooms.models import Room


class RoomDetailView(RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
