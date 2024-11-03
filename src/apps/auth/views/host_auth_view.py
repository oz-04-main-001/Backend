from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth.serializers.host_auth_serializer import HostRegisterSerializer


@extend_schema(tags=["Host"])
class HostRegistrationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=HostRegisterSerializer,
        summary="호스트 등록 API",
        description="해당 API는 호스트 등록을 위한 api입니다.",
    )
    def post(self, request):
        if hasattr(request.user, "host"):
            return Response({"detail": "이미 호스트로 등록된 유저입니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = HostRegisterSerializer(data=request.data)

        if serializer.is_valid():
            # 여기서 자동으로 pending 상태로 저장
            serializer.save(user=request.user, verification_status="pending")  # 기본값으로 pending 설정
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
