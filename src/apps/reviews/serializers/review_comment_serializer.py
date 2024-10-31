from rest_framework import serializers
from apps.reviews.models import Comment, Review



class CommentSerializer(serializers.ModelSerializer):
    # 댓글에 대한 리뷰를 참조할 수 있도록 설정
    review = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
      model = Comment
      fields = ['id','review','user','contents','created_at', 'updated_at']
      read_only_fields = ('id','review','user','created_at', 'updated_at')

    def create(self, validated_data):
        # 숙소 고정
        review_id = self.context['view'].kwargs['review_id']
        validated_data['review'] = Review.objects.get(pk=review_id)  # 리뷰 객체를 가져와서 설정
        # 요청한 사용자 설정
        validated_data['user'] = self.context['request'].user  # 현재 요청한 사용자를 user 필드에 할당
        return super().create(validated_data)  # 댓글 생성


