from django.urls import path

from . import views
from .views import review_comment_view, review_view

app_name = "reviews"  # 앱 이름 설정

urlpatterns = [
    path("", review_view.ReviewsView.as_view(), name="reviews"),
    path("<int:pk>/", review_view.ReviewDetailView.as_view(), name="review_detail"),
    path("<int:review_id>/comments/", review_comment_view.ReviewCommentView.as_view(), name="review_comments"),
    path(
        "comments/<int:pk>/", review_comment_view.CommentDeleteView.as_view(), name="comment_delete"
    ),  # 특정 댓글 삭제
]
