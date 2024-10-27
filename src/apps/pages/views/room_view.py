from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.pages.serializers.room_serializer import RoomDetailSerializer
from apps.rooms.models import Room


@extend_schema(tags=["Guest"])
class RoomDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer

    @extend_schema(
        summary="룸 디테일 -> /{id}: room_id",
        description="",
        responses={200: RoomDetailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
