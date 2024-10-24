from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
)
from apps.accommodations.serializers.accommodation_serializer import (
    AccommodationImageSerializer,
    AccommodationImageUpdateSerializer,
    AccommodationSerializer,
    AccommodationTypeSerializer,
    AccommodationUpdateSerializer,
    GPSInfoSerializer,
)
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.users.models import BusinessUser

User = get_user_model()


class BaseAccommodationView:
    """기본 숙소 뷰 - 호스트 생성 로직"""

    permission_classes = [AllowAny]

    def get_or_create_host(self):
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            raise ValidationError({"error": "슈퍼유저가 존재하지 않습니다. 먼저 슈퍼유저를 생성해주세요."})

        host, created = BusinessUser.objects.get_or_create(user=superuser)
        if created:
            host.business_name = "Default Business"
            host.business_registration_number = "000-00-00000"
            host.save()
        return host


class AccommodationListCreateView(BaseAccommodationView, generics.ListCreateAPIView):
    """숙소 목록 조회 및 생성"""

    queryset = Accommodation.objects.all().select_related("accommodationtype", "gps_info").prefetch_related("images")
    serializer_class = AccommodationSerializer
    permission_classes = [AllowAny]

    def validate_accommodation_data(self, request_data):
        if not request_data.get("name"):
            raise ValidationError({"name": "숙소 이름은 필수입니다."})
        if not request_data.get("phone_number"):
            raise ValidationError({"phone_number": "전화번호는 필수입니다."})
        if not request_data.get("accommodation_type"):
            raise ValidationError({"accommodation_type": "숙소 유형은 필수입니다."})
        if not request_data.get("gps_info"):
            raise ValidationError({"gps_info": "위치 정보는 필수입니다."})
        if not request_data.get("amenities"):
            raise ValidationError({"amenities": "부대시설 정보는 필수입니다."})

    def process_accommodation_type(self, type_data):
        """숙소 타입 처리 - 기존 타입 사용 또는 새 커스텀 타입 생성"""
        if isinstance(type_data, dict):
            # 새로운 커스텀 타입 생성
            type_data["is_custom"] = True  # 커스텀 타입임을 표시
            type_serializer = AccommodationTypeSerializer(data=type_data)
            if type_serializer.is_valid():
                return type_serializer.save()
            raise ValidationError(type_serializer.errors)
        else:
            # 기존 타입 ID 사용
            return get_object_or_404(AccommodationType, id=type_data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.validate_accommodation_data(request.data)

        # 1. 숙소 타입 처리 (커스텀 타입 지원)
        accommodation_type = self.process_accommodation_type(request.data.get("accommodation_type"))

        # 2. GPS 정보 처리
        gps_info_data = request.data.get("gps_info")
        gps_info_serializer = GPSInfoSerializer(data=gps_info_data)
        if gps_info_serializer.is_valid():
            gps_info = gps_info_serializer.save()
        else:
            raise ValidationError(gps_info_serializer.errors)

        # 3. 숙소 생성
        host = self.get_or_create_host()
        accommodation_data = {
            **request.data,
            "host": host.id,
            "accommodationtype": accommodation_type.id,
            "gps_info": gps_info.id,
        }
        accommodation_serializer = self.get_serializer(data=accommodation_data)
        if accommodation_serializer.is_valid():
            accommodation = accommodation_serializer.save()
        else:
            raise ValidationError(accommodation_serializer.errors)

        # 4. 이미지 처리
        images = request.FILES.getlist("images", [])
        total_size = sum(image.size for image in images)

        if total_size > 50 * 1024 * 1024:  # 50MB
            raise ValidationError({"images": "전체 이미지 크기가 50MB를 초과할 수 없습니다."})

        image_instances = []
        for image in images:
            if not image.content_type.startswith("image/"):
                raise ValidationError({"images": f"{image.name}은(는) 유효한 이미지 파일이 아닙니다."})
            if image.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError({"images": f"{image.name}의 크기가 10MB를 초과합니다."})
            image_instances.append(Accommodation_Image(accommodation=accommodation, image=image))
        if image_instances:
            Accommodation_Image.objects.bulk_create(image_instances)

        # 5. 부대시설 처리
        amenities_data = request.data.get("amenities", [])
        amenity_instances = []
        for amenity_id in amenities_data:
            amenity = get_object_or_404(Amenity, id=amenity_id)
            amenity_instances.append(AccommodationAmenity(accommodation=accommodation, amenity=amenity))
        if amenity_instances:
            AccommodationAmenity.objects.bulk_create(amenity_instances)

        return Response(accommodation_serializer.data, status=status.HTTP_201_CREATED)


class AccommodationRetrieveUpdateDestroyView(BaseAccommodationView, generics.RetrieveUpdateDestroyAPIView):
    """숙소 상세 조회, 수정, 삭제"""

    queryset = Accommodation.objects.all().select_related("accommodationtype", "gps_info").prefetch_related("images")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AccommodationUpdateSerializer
        return AccommodationSerializer

    def validate_update_data(self, request_data, partial=False):
        if not partial:
            if not request_data.get("name"):
                raise ValidationError({"name": "숙소 이름은 필수입니다."})
            if not request_data.get("phone_number"):
                raise ValidationError({"phone_number": "전화번호는 필수입니다."})

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        self.validate_update_data(request.data, partial)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.images.all().delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# 이미지 관리
class AccommodationImageView(BaseAccommodationView, generics.ListCreateAPIView, generics.DestroyAPIView):
    """숙소 이미지 관리"""

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AccommodationImageUpdateSerializer
        return AccommodationImageSerializer  # GET 요청시 기본 시리얼라이저 사용

    def get_queryset(self):
        return Accommodation_Image.objects.filter(accommodation_id=self.kwargs["pk"])

    def get_object(self):
        # DestroyAPIView에서 사용
        accommodation = get_object_or_404(Accommodation, pk=self.kwargs["pk"])
        return accommodation

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = AccommodationImageSerializer(queryset, many=True)  # 조회시에는 기본 시리얼라이저
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        accommodation = get_object_or_404(Accommodation, pk=self.kwargs["pk"])

        # 이미지 처리 및 검증
        if "images" not in request.FILES:
            raise ValidationError({"images": "이미지 파일은 필수입니다."})

        images = request.FILES.getlist("images")
        total_size = sum(image.size for image in images)

        if total_size > 50 * 1024 * 1024:
            raise ValidationError({"images": "전체 이미지 크기가 50MB를 초과할 수 없습니다."})

        # 기존 이미지 삭제 여부 확인
        if request.data.get("delete_existing", "").lower() == "true":
            accommodation.images.all().delete()

        # 새 이미지 추가
        image_instances = []
        for image in images:
            serializer = AccommodationImageUpdateSerializer(data={"image": image})
            if serializer.is_valid(raise_exception=True):
                image_instances.append(Accommodation_Image(accommodation=accommodation, image=image))

        created_images = Accommodation_Image.objects.bulk_create(image_instances)
        response_serializer = AccommodationImageSerializer(created_images, many=True)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        accommodation = self.get_object()
        accommodation.images.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# GPS 정보 관리
class GPSInfoView(BaseAccommodationView, generics.RetrieveUpdateAPIView):
    """GPS 정보 조회 및 수정"""

    serializer_class = GPSInfoSerializer
    queryset = Accommodation.objects.all().select_related("gps_info")

    def get_object(self):
        accommodation = get_object_or_404(Accommodation, id=self.kwargs.get("accommodation_id"))
        return accommodation.gps_info

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # GPS 좌표 검증
        location = request.data.get("location")
        if location and isinstance(location, dict):
            try:
                coordinates = location.get("coordinates", [])
                if len(coordinates) != 2:
                    raise ValidationError({"location": "올바른 좌표 형식이 아닙니다."})

                longitude, latitude = coordinates
                if not (-90 <= latitude <= 90):
                    raise ValidationError({"location": "위도는 -90에서 90 사이의 값이어야 합니다."})
                if not (-180 <= longitude <= 180):
                    raise ValidationError({"location": "경도는 -180에서 180 사이의 값이어야 합니다."})
            except (TypeError, ValueError):
                raise ValidationError({"location": "올바른 좌표 형식이 아닙니다."})

        # 주소 정보 검증
        if not partial:
            if not request.data.get("city"):
                raise ValidationError({"city": "도시명은 필수입니다."})
            if not request.data.get("states"):
                raise ValidationError({"states": "시/도는 필수입니다."})
            if not request.data.get("road_name"):
                raise ValidationError({"road_name": "도로명은 필수입니다."})
            if not request.data.get("address"):
                raise ValidationError({"address": "주소는 필수입니다."})

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


# 숙소 타입 관리
# class AccommodationTypeView(BaseAccommodationView, generics.RetrieveUpdateAPIView):
#     """숙소 타입 정보 조회 및 수정"""
#     serializer_class = AccommodationTypeSerializer
#     queryset = Accommodation.objects.all().select_related("accommodationtype")
#
#     def get_object(self):
#         accommodation = get_object_or_404(Accommodation, id=self.kwargs['pk'])
#         return accommodation.accommodationtype
#
#     @transaction.atomic
#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)
