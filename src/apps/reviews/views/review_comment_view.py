from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.reviews.models import Comment
from apps.reviews.serializers.review_comment_serializer import CommentSerializer


# 댓글 리스트 조회 및 생성, 삭제 가능
class ReviewCommentView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # 주어진 리뷰 ID에 대한 댓글만 조회
        review_id = self.kwargs['review_id']
        return Comment.objects.filter(review_id=review_id)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="댓글 리스트",
        description="리뷰별 댓글 리스트를 조회합니다.",
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="댓글 생성",
        description="리뷰에 대한 댓글을 생성합니다.",
        responses={201: CommentSerializer},
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# 특정 댓글 삭제를 위한 뷰
class CommentDeleteView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @extend_schema(
        tags=['Guest-Reviews'],
        summary="댓글 삭제",
        description="특정 댓글을 삭제합니다.",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    def perform_destroy(self, instance):
        instance.delete()
