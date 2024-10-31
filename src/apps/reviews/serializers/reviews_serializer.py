from django.db import transaction
from rest_framework import serializers
from apps.reviews.models import Rating, Review, Comment
from apps.reviews.serializers.review_comment_serializer import CommentSerializer


# 리뷰 생성과, 리스트 반환 시리얼라이저
class ReviewListCreateSerializer(serializers.ModelSerializer):
    rating = serializers.CharField()

    class Meta:
        model = Review
        fields = [
            "id",
            "guest",
            "accommodation",
            "contents",
            "created_at",
            "rating",
        ]
        read_only_fields = ["guest"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)  # 기본 표현을 가져옴
        representation['rating'] = instance.rating.rating if instance.rating else None  # 평점 값 설정
        return representation  # 수정된 표현 반환



    def create(self, validated_data):
        rating_value = validated_data.pop("rating")  # 별점 값을 추출

        with transaction.atomic():  # 트랜잭션 시작
            review = Review.objects.create(
                guest=self.context['request'].user,
                accommodation=validated_data["accommodation"],
                contents=validated_data["contents"]
            )
            Rating.objects.create(review=review, rating=rating_value)  # 리뷰와 별점 연결

        return review



# 리뷰 상세,수정,삭제 시리얼라이저
class ReviewDetailUpdateDeleteSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    comment = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["id", "guest", "accommodation","rating","comment"]

    def get_rating(self, obj):
        return obj.rating.rating if hasattr(obj.rating, "rating") else None

    def get_comment(self, obj):
        serializer = CommentSerializer(obj, many=True)
        return serializer.data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


