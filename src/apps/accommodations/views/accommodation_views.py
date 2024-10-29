import json

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import filters, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import DictField, FileField, ImageField, ListField
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps import amenities
from apps.accommodations.models import (
    Accommodation,
    Accommodation_Image,
    AccommodationType,
    GPS_Info,
    RefundPolicy,
)
from apps.accommodations.serializers import accommodation_serializer as serializers
from apps.accommodations.serializers.accommodation_serializer import (
    AccommodationImageSerializer,
    AccommodationImageUpdateSerializer,
    AccommodationSerializer,
    AccommodationTypeSerializer,
    AccommodationUpdateSerializer,
    GPSInfoSerializer,
    RefundPolicySerializer,
)
from apps.amenities.models import AccommodationAmenity, Amenity
from apps.amenities.serializers.amenities_serializers import (
    AccommodationAmenitySerializer,
    AmenitySerializer,
)
from apps.common.choices import AMENITY_CHOICES
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


class AccommodationListCreateView(BaseAccommodationView, APIView):
    """숙소 목록 조회 및 생성"""

    parser_classes = (MultiPartParser, FormParser)
    serializer_class = AccommodationSerializer
    permission_classes = [AllowAny]  # [isauthentication, ishost]

    @extend_schema(
        request=inline_serializer(
            name="AccommodationCreateRequest",
            fields={
                "accommodation": serializers.AccommodationSerializer(),
                "images": ListField(child=ImageField(), help_text="숙소에 업로드할 이미지 파일들"),
                "accommodation_type": serializers.AccommodationTypeSerializer(),
                "GPS_info": serializers.GPSInfoSerializer(),
                "amenities": inline_serializer(
                    name="AmenitiesRequest",
                    fields={"new": AmenitySerializer(many=True), "default": AccommodationAmenitySerializer(many=True)},
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=serializers.AccommodationSerializer, description="숙소가 성공적으로 생성되었습니다."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response={"type": "object", "properties": {"detail": {"type": "string"}, "code": {"type": "string"}}},
                description="잘못된 요청: 입력 값이 유효하지 않습니다.",
            ),
        },
        summary="숙소 생성",
        description="새로운 숙소를 생성하며, 이미지, 숙소 유형, GPS 정보 및 편의 시설을 함께 등록합니다.",
    )
    def post(self, request):
        try:
            data = {
                "accommodation": json.loads(request.data.get("accommodation")),
                "accommodation_type": json.loads(request.data.get("accommodation_type")),
                "GPS_info": json.loads(request.data.get("GPS_info")),
                "amenities": json.loads(request.data.get("amenities")),
                "images": request.FILES.getlist("images"),
            }

            request_data = self.validate_accommodation_data(data)

            # 1. create dummy host
            host = self.get_or_create_host()

            # 2. create accommodation model
            accommodation_data = request_data.get("accommodation")
            accommodation_serializer = serializers.AccommodationSerializer(data=accommodation_data)
            if not accommodation_serializer.is_valid():
                return Response(accommodation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            accommodation = accommodation_serializer.save(host=host)

            # 2. 이미지 처리
            image_data = [{"image": image, "accommodation": accommodation.id} for image in request_data["images"]]
            image_response_data = []
            for data in image_data:
                image_serializer = serializers.AccommodationImageSerializer(data=data)
                if not image_serializer.is_valid():
                    return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                image_serializer.save()
                image_response_data.append(image_serializer.data)

            # 3. create accommodation type
            type_serializer = serializers.AccommodationTypeSerializer(
                data=request_data.get("accommodation_type"),
            )
            if not type_serializer.is_valid():
                return Response(type_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            type_serializer.save(accommodation=accommodation)

            # 4. create GPS Info
            gps_serializer = serializers.GPSInfoSerializer(data=request_data.get("GPS_info"))
            if not gps_serializer.is_valid():
                return Response(gps_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            gps_serializer.save(accommodation=accommodation)

            # 5. 어메니티 처리
            amenities_data = request_data["amenities"]  # get 대신 직접 접근
            new_amenities = amenities_data["new"]  # dictionary key로 직접 접근
            default_amenities = amenities_data["default"]
            amenity_response_data = []
            if new_amenities:
                for data in new_amenities:
                    new_amenity_serializer = AmenitySerializer(data=data)
                    if not new_amenity_serializer.is_valid():
                        return Response(new_amenity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    created_amenity = new_amenity_serializer.save()

                    # 새로 생성된 어메니티를 숙소와 연결
                    AccommodationAmenity.objects.create(
                        accommodation=accommodation, amenity=created_amenity, custom_value=None  # 또는 필요한 값
                    )
                    amenity_response_data.append(new_amenity_serializer.data)

            if default_amenities:
                for default_amenity in default_amenities:
                    amenity_id = default_amenity["amenity_id"]  # get 대신 직접 접근
                    if amenity_id:
                        try:
                            amenity = Amenity.objects.get(id=amenity_id)
                            AccommodationAmenity.objects.create(
                                accommodation=accommodation,
                                amenity=amenity,
                                custom_value=default_amenity.get("custom_value", None),
                            )
                        except Amenity.DoesNotExist:
                            return Response(
                                {"error": f"Amenity with id {amenity_id} does not exist"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
            return Response(
                {
                    "accommodation": accommodation_serializer.data,
                    "\n" "accommodation_type": type_serializer.data,
                    "\n" "gps_info": gps_serializer.data,
                    "\n" "amenities": amenity_response_data,
                    "\n" "images": image_response_data,
                },
                status=status.HTTP_201_CREATED,
            )

        except json.JSONDecodeError as e:
            return Response({"error": "잘못된 JSON 형식입니다.", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    def validate_accommodation_data(self, request_data):
        if not request_data.get("accommodation"):
            raise ValidationError({"accommodation": "숙소 정보가 누락되었습니다."})
        if not request_data.get("images"):
            raise ValidationError({"images": "숙소 이미지가 누락되었습니다."})
        if not request_data.get("accommodation_type"):
            raise ValidationError({"accommodation_type": "숙소 유형 정보가 누락되었습니다."})
        if not request_data.get("GPS_info"):
            raise ValidationError({"GPS_info": "숙소 위치 정보가 누락되었습니다."})
        if not request_data.get("amenities"):
            raise ValidationError({"amenities": "어메니티 정보가 누락되었습니다."})

        return request_data

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


class AmenityChoicesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="어메니티 선택지 목록 조회",
        description="사용 가능한 어메니티 선택지 목록을 반환합니다.",
        responses={
            200: {
                "type": "array",
                "items": {"type": "object", "properties": {"value": {"type": "string"}, "label": {"type": "string"}}},
            }
        },
    )
    def get(self, request):
        choices = [choice[0] for choice in AMENITY_CHOICES]  # value만 반환
        return Response(choices)


# views.py에 추가
# class RefundPolicyView(generics.RetrieveUpdateDestroyAPIView):
#     """환불 정책 조회, 수정, 삭제"""
#
#     serializer_class = RefundPolicySerializer
#     permission_classes = [AllowAny]
#
#     def get_queryset(self):
#         return RefundPolicy.objects.filter(accommodation_id=self.kwargs["accommodation_id"])
#
#     def get_object(self):
#         accommodation_id = self.kwargs["accommodation_id"]
#         return get_object_or_404(RefundPolicy, accommodation_id=accommodation_id)

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
