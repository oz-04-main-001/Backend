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
    AccommodationSerializer,
    AccommodationTypeSerializer,
    GPSInfoSerializer,
)
from apps.users.models import BusinessUser

User = get_user_model()


class BaseAccommodationView:
    """기본 숙소 뷰 - 호스트 생성 로직"""

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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.validate_accommodation_data(request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        host = self.get_or_create_host()
        accommodation = serializer.save(host=host)

        # 이미지 처리 및 검증
        images = self.request.FILES.getlist("images", [])
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


class AccommodationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """숙소 상세 조회, 수정, 삭제"""

    queryset = Accommodation.objects.all().select_related("accommodationtype", "gps_info").prefetch_related("images")
    serializer_class = AccommodationSerializer
    permission_classes = [AllowAny]

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

        # 이미지 처리 및 검증
        if "images" in request.FILES:
            images = request.FILES.getlist("images")
            total_size = sum(image.size for image in images)

            if total_size > 50 * 1024 * 1024:
                raise ValidationError({"images": "전체 이미지 크기가 50MB를 초과할 수 없습니다."})

            image_instances = []
            for image in images:
                if not image.content_type.startswith("image/"):
                    raise ValidationError({"images": f"{image.name}은(는) 유효한 이미지 파일이 아닙니다."})
                if image.size > 10 * 1024 * 1024:
                    raise ValidationError({"images": f"{image.name}의 크기가 10MB를 초과합니다."})
                image_instances.append(Accommodation_Image(accommodation=instance, image=image))
            Accommodation_Image.objects.bulk_create(image_instances)

        return Response(serializer.data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.images.all().delete()  # 연관된 이미지 파일도 삭제
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccommodationSearchView(generics.ListAPIView):
    """숙소 검색"""

    serializer_class = AccommodationSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description", "gps_info__city", "gps_info__states", "accommodationtype__type_name"]

    def get_queryset(self):
        queryset = (
            Accommodation.objects.all().select_related("accommodationtype", "gps_info").prefetch_related("images")
        )

        min_rating = self.request.query_params.get("min_rating")
        accommodation_type = self.request.query_params.get("type")

        if min_rating:
            try:
                min_rating = float(min_rating)
                if not (0 <= min_rating <= 5):
                    raise ValidationError({"min_rating": "평점은 0에서 5 사이의 값이어야 합니다."})
                queryset = queryset.filter(average_rating__gte=min_rating)
            except ValueError:
                raise ValidationError({"min_rating": "유효한 숫자를 입력해주세요."})

        if accommodation_type:
            queryset = queryset.filter(accommodationtype__type_name=accommodation_type)

        return queryset


class AccommodationsByLocationView(generics.ListAPIView):
    """위치 기반 숙소 검색"""

    serializer_class = AccommodationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        city = self.kwargs.get("city")
        state = self.kwargs.get("state")

        if not city and not state:
            raise ValidationError({"error": "도시 또는 주/도를 입력해주세요."})

        return (
            Accommodation.objects.filter(Q(gps_info__city__icontains=city) | Q(gps_info__states__icontains=state))
            .select_related("accommodationtype", "gps_info")
            .prefetch_related("images")
        )


class AccommodationBulkCreateView(BaseAccommodationView, APIView):
    """여러 숙소 동시 생성"""

    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        accommodations_data = request.data.get("accommodations", [])

        if not accommodations_data:
            raise ValidationError({"error": "생성할 숙소 데이터가 없습니다."})

        if len(accommodations_data) > 10:  # 최대 생성 개수 제한
            raise ValidationError({"error": "한 번에 최대 10개의 숙소만 생성할 수 있습니다."})

        created_accommodations = []
        host = self.get_or_create_host()

        for data in accommodations_data:
            serializer = AccommodationSerializer(data=data)
            if serializer.is_valid():
                accommodation = serializer.save(host=host)
                created_accommodations.append(serializer.data)
            else:
                raise ValidationError(serializer.errors)

        return Response(created_accommodations, status=status.HTTP_201_CREATED)


class AccommodationTypeListCreateView(generics.ListCreateAPIView):
    """숙소 타입 목록 조회 및 생성"""

    queryset = AccommodationType.objects.all()
    serializer_class = AccommodationTypeSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if not request.data.get("type_name"):
            raise ValidationError({"type_name": "숙소 유형 이름은 필수입니다."})
        return super().create(request, *args, **kwargs)


class AccommodationTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """숙소 타입 상세 조회, 수정, 삭제"""

    queryset = AccommodationType.objects.all()
    serializer_class = AccommodationTypeSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        if not request.data.get("type_name"):
            raise ValidationError({"type_name": "숙소 유형 이름은 필수입니다."})
        return super().update(request, *args, **kwargs)


class AccommodationTypeCustomCreateView(APIView):
    """사용자 정의 숙소 타입 생성"""

    permission_classes = [AllowAny]

    def post(self, request):
        if not request.data.get("type_name"):
            raise ValidationError({"type_name": "숙소 유형 이름은 필수입니다."})

        data = request.data.copy()
        data["is_customized"] = True
        serializer = AccommodationTypeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccommodationTypeStatisticsView(APIView):
    """숙소 타입별 통계"""

    permission_classes = [AllowAny]

    def get(self, request):
        statistics = {}
        accommodation_types = AccommodationType.objects.all()

        if not accommodation_types.exists():
            return Response({"message": "등록된 숙소 유형이 없습니다."})

        for acc_type in accommodation_types:
            accommodations = Accommodation.objects.filter(accommodationtype__type_name=acc_type.type_name)
            statistics[acc_type.type_name] = {
                "total_accommodations": accommodations.count(),
                "average_rating": accommodations.aggregate(Avg("average_rating"))["average_rating__avg"] or 0.0,
            }
        return Response(statistics)


class AccommodationImageListCreateView(generics.ListCreateAPIView):
    """숙소 이미지 목록 조회 및 생성"""

    queryset = Accommodation_Image.objects.all()
    serializer_class = AccommodationImageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if "image" not in request.FILES:
            raise ValidationError({"image": "이미지 파일은 필수입니다."})
        return super().create(request, *args, **kwargs)


class AccommodationImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """숙소 이미지 상세 조회, 수정, 삭제"""

    queryset = Accommodation_Image.objects.all()
    serializer_class = AccommodationImageSerializer
    permission_classes = [AllowAny]


class AccommodationImageBulkUploadView(generics.CreateAPIView):
    """여러 이미지 동시 업로드"""

    serializer_class = AccommodationImageSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        accommodation_id = kwargs.get("accommodation_id")
        accommodation = get_object_or_404(Accommodation, id=accommodation_id)

        images = request.FILES.getlist("images", [])
        if not images:
            raise ValidationError({"error": "업로드할 이미지가 없습니다."})

        if len(images) > 10:
            raise ValidationError({"error": "한 번에 최대 10개의 이미지만 업로드할 수 있습니다."})

        total_size = sum(image.size for image in images)
        if total_size > 50 * 1024 * 1024:  # 50MB
            raise ValidationError({"error": "전체 이미지 크기가 50MB를 초과할 수 없습니다."})

        image_instances = []
        for image in images:
            if not image.content_type.startswith("image/"):
                raise ValidationError({"error": f"{image.name}은(는) 유효한 이미지 파일이 아닙니다."})

            if image.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError({"error": f"{image.name}의 크기가 10MB를 초과합니다."})

            image_instances.append(Accommodation_Image(accommodation=accommodation, image=image))

            created_images = Accommodation_Image.objects.bulk_create(image_instances)
            return Response(self.get_serializer(created_images, many=True).data, status=status.HTTP_201_CREATED)


class GPSInfoRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """GPS 정보 조회 및 수정"""

    serializer_class = GPSInfoSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        accommodation_id = self.kwargs.get("accommodation_id")
        return get_object_or_404(GPS_Info, accommodation_id=accommodation_id)

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
