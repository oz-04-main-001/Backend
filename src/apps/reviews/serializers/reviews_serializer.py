from rest_framework import serializers
from apps.reviews.models import Review, Rating


# 평점 시리얼라이저
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


# 리뷰 생성과, 리스트 반환 시리얼라이저
class ReviewListCreateSerializer(serializers.ModelSerializer):
    rating = RatingSerializer()
    class Meta:
        model = Review
        fields = [
            'guest',
            'accommodation',
            'contents',
            'created_at',
            'rating',
        ]

    def create(self, validated_data):
        rating_data = validated_data.pop('rating', None)
        review = Review.objects.create(**validated_data)
        if rating_data:
            # 평점 생성
            Rating.objects.create(review=review, **rating_data)
            # 숙소 평점 업데이트 처리 추가예정
        return review


# 리뷰 상세,수정,삭제 시리얼라이저
class ReviewDetailUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id']


    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

