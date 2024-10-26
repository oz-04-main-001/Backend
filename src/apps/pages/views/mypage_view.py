from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.pages.serializers.mypage_serializer import MyPageSerializer


@extend_schema(tags=["Guest"])
class MyBookingListView(ListAPIView):
    serializer_class = MyPageSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={})
        serializer.is_valid(raise_exception=True)  # 유효성 검사
        return Response(serializer.data)  # 직렬화된 데이터 반환
