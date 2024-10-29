from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.reviews.models import Review
from apps.reviews.serializers.reviews_serializer import (
    ReviewDetailUpdateDeleteSerializer,
    ReviewListCreateSerializer,
)


# 리뷰 생성과, 리스트 반환 api
class ReviewListCreateView(ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


# 리뷰 상세,수정,삭제 api
class ReviewUpdateDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailUpdateDeleteSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
