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
    RoomOptionUpdateSerializer,
)
from apps.common.permissions.host_permission import IsHost
from apps.rooms.models import Room


# Amenity views
@extend_schema(tags=["Host"])
class AmenityListView(generics.ListAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]


@extend_schema(tags=["Host"])
class AccommodationAmenityView(generics.RetrieveUpdateDestroyAPIView):
    """숙소별 부대시설 조회, 수정, 삭제"""

    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]

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
class OptionListView(generics.ListAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]


@extend_schema(tags=["Host"])
class RoomOptionView(generics.RetrieveUpdateDestroyAPIView):
    """룸별 옵션 조회, 수정, 삭제"""

    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]
    serializer_class = OptionSerializer

    def get_queryset(self):
        return Option.objects.filter(roomoption__room_id=self.kwargs["room_id"])

    def get_object(self):
        room_id = self.kwargs["room_id"]
        get_object_or_404(Room, id=room_id)  # 방이 존재하는지 확인
        return Option.objects.filter(roomoption__room_id=room_id)

    def retrieve(self, request, *args, **kwargs):
        """옵션 조회"""
        options = self.get_object()
        serializer = self.get_serializer(options, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """옵션 수정"""
        room_id = self.kwargs["room_id"]
        room = get_object_or_404(Room, id=room_id)

        options_data = request.data.get("options", [])
        if not options_data:
            raise ValidationError({"options": "옵션 정보는 필수입니다."})

        # 기존 옵션 관계 삭제
        RoomOption.objects.filter(room=room).delete()

        # 새로운 옵션 생성 및 연결
        for option_data in options_data:
            if isinstance(option_data, dict):
                # 새로운 커스텀 옵션 생성
                option = Option.objects.create(
                    name=option_data["name"], category=option_data.get("category", "extra"), is_custom=True
                )
            else:
                # 기존 옵션 연결
                option = get_object_or_404(Option, id=option_data)

            RoomOption.objects.create(room=room, option=option)

        # 수정된 옵션 목록 반환
        updated_options = self.get_queryset()
        serializer = self.get_serializer(updated_options, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """옵션 삭제"""
        room_id = self.kwargs["room_id"]
        room = get_object_or_404(Room, id=room_id)

        # 특정 옵션만 삭제하는 경우
        option_ids = request.query_params.getlist("option_ids", [])
        if option_ids:
            try:
                option_ids = [int(id) for id in option_ids]
                RoomOption.objects.filter(room=room, option_id__in=option_ids).delete()
            except ValueError:
                raise ValidationError({"detail": "잘못된 옵션 ID 형식입니다."})
        else:
            # 모든 옵션 삭제
            RoomOption.objects.filter(room=room).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# Custom views
@extend_schema(tags=["Host"])
class CustomOptionListView(generics.ListAPIView):
    serializer_class = OptionSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated, IsHost]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Option.objects.filter(is_custom=True)

        return Option.objects.filter(is_custom=True, roomoption__room__accommodation__host=self.request.user).distinct()
