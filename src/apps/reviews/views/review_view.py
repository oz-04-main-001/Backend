from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.reviews.models import Review
from apps.reviews.serializers.reviews_serializer import (
    ReviewDetailUpdateDeleteSerializer,
    ReviewListCreateSerializer,
)


# 리뷰 생성과, 리스트 반환 API
class ReviewsView(ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="리뷰 리스트",
        description="리뷰 목록을 조회합니다.",
        responses={200: ReviewListCreateSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="리뷰 생성",
        description="새로운 리뷰를 작성합니다.",
        responses={201: ReviewListCreateSerializer()},
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # 현재 로그인한 사용자를 guest로 설정하여 리뷰 생성
        serializer.save(guest=self.request.user)


# 리뷰 상세, 수정, 삭제 API
class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailUpdateDeleteSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="리뷰 디테일 조회",
        description="특정 리뷰의 상세 정보를 조회합니다.",
        responses={200: ReviewDetailUpdateDeleteSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="리뷰 수정",
        description="리뷰를 수정합니다.",
        responses={204: ReviewDetailUpdateDeleteSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="리뷰 수정",
        description="리뷰를 수정합니다.",
        responses={204: ReviewDetailUpdateDeleteSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="리뷰 삭제",
        description="리뷰를 삭제합니다.",
        responses={204: ReviewDetailUpdateDeleteSerializer()},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)