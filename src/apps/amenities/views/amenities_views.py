# 20241023 수정
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.amenities.models import AccommodationAmenity, Amenity, Option, RoomOption
from apps.amenities.serializers.amenities_serializers import (
    AccommodationAmenityUpdateSerializer,
    AmenitySerializer,
    DetailedRoomOptionSerializer,
    OptionSerializer,
    RoomOptionSerializer,
)


# Amenity views
@extend_schema(tags=["Host"])
class AmenityListView(generics.ListAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]


@extend_schema(tags=["Host"])
class AccommodationAmenityView(generics.RetrieveUpdateDestroyAPIView):
    """숙소별 부대시설 조회, 수정, 삭제"""

    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AccommodationAmenityUpdateSerializer
        return AccommodationAmenityUpdateSerializer

    def get_queryset(self):
        return AccommodationAmenity.objects.filter(accommodation_id=self.kwargs["accommodation_id"]).select_related(
            "amenity"
        )

    def get_object(self):
        accommodation_id = self.kwargs["accommodation_id"]
        amenities = AccommodationAmenity.objects.filter(accommodation_id=accommodation_id).select_related("amenity")
        if not amenities.exists():
            raise ValidationError({"detail": "해당 숙소의 부대시설이 없습니다."})
        return amenities

    def retrieve(self, request, *args, **kwargs):
        """부대시설 조회"""
        amenities = self.get_object()
        serializer = self.get_serializer(amenities, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """부대시설 수정"""
        accommodation_id = self.kwargs["accommodation_id"]

        # 기존 부대시설 삭제
        AccommodationAmenity.objects.filter(accommodation_id=accommodation_id).delete()

        # 새로운 부대시설 추가
        amenities_data = request.data.get("amenities", [])
        if not amenities_data:
            raise ValidationError({"amenities": "부대시설 정보는 필수입니다."})

        amenity_instances = []
        for amenity_data in amenities_data:
            if isinstance(amenity_data, dict):
                if "id" in amenity_data:
                    # 기존 부대시설 사용
                    amenity = get_object_or_404(Amenity, id=amenity_data["id"])
                    custom_value = amenity_data.get("custom_value", "")
                else:
                    # 새로운 커스텀 부대시설 생성
                    amenity = Amenity.objects.create(
                        name=amenity_data["name"],
                        category=amenity_data.get("category", "basic"),
                        description=amenity_data.get("description", ""),
                        icon=amenity_data.get("icon", ""),
                        is_custom=True,
                    )
                    custom_value = amenity_data.get("custom_value", "")
            else:
                # amenity_data가 ID인 경우
                amenity = get_object_or_404(Amenity, id=amenity_data)
                custom_value = ""

            amenity_instances.append(
                AccommodationAmenity(accommodation_id=accommodation_id, amenity=amenity, custom_value=custom_value)
            )

        AccommodationAmenity.objects.bulk_create(amenity_instances)

        # 업데이트된 데이터 반환
        updated_amenities = self.get_queryset()
        serializer = AccommodationAmenityUpdateSerializer(updated_amenities, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """부대시설 삭제"""
        amenities = self.get_object()

        # 특정 부대시설만 삭제하는 경우
        amenity_ids = request.query_params.getlist("amenity_ids", [])
        if amenity_ids:
            try:
                amenity_ids = [int(id) for id in amenity_ids]
                deleted_count = amenities.filter(amenity_id__in=amenity_ids).delete()[0]
                if deleted_count == 0:
                    return Response({"detail": "삭제할 부대시설을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                raise ValidationError({"detail": "잘못된 부대시설 ID 형식입니다."})
        else:
            # 모든 부대시설 삭제
            amenities.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# Option views
@extend_schema(tags=["Host"])
class OptionListCreateView(generics.ListCreateAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        try:
            serializer.save(is_custom=True)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({"detail": "An option with this name already exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class OptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        if instance.roomoption_set.exists():
            raise ValidationError("Cannot delete option that is in use")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# RoomOption views
@extend_schema(tags=["Host"])
class RoomOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return RoomOption.objects.filter(room_id=self.kwargs["room_id"])

    def perform_create(self, serializer):
        try:
            serializer.save(room_id=self.kwargs["room_id"])
        except IntegrityError:
            raise ValidationError("This option is already added to the room")

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
class RoomOptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoomOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return RoomOption.objects.filter(room_id=self.kwargs["room_id"])

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


@extend_schema(tags=["Host"])
class DetailedRoomOptionListView(generics.ListAPIView):
    serializer_class = DetailedRoomOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return RoomOption.objects.filter(room_id=room_id).select_related("option")


# Custom views
@extend_schema(tags=["Host"])
class CustomAmenityListView(generics.ListAPIView):
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Amenity.objects.filter(is_custom=True)

        return Amenity.objects.filter(
            is_custom=True, accommodationamenity__accommodation__host=self.request.user
        ).distinct()


@extend_schema(tags=["Host"])
class CustomOptionListView(generics.ListAPIView):
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Option.objects.filter(is_custom=True)

        return Option.objects.filter(is_custom=True, roomoption__room__accommodation__host=self.request.user).distinct()
