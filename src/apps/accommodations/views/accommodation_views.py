from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import BusinessUser

from apps.accommodations.models import Accommodation, Accommodation_Image, AccommodationType, GPS_Info
from apps.accommodations.serializers.accommodation_serializer import (
    AccommodationImageSerializer,
    AccommodationSerializer,
    AccommodationTypeSerializer,
    GPSInfoSerializer,
)

User = get_user_model()


class AccommodationListCreateView(generics.ListCreateAPIView):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # 슈퍼유저를 가져옵니다.
        superuser = User.objects.filter(is_superuser=True).first()

        if not superuser:
            raise ValueError("슈퍼유저가 존재하지 않습니다. 먼저 슈퍼유저를 생성해주세요.")

        # 슈퍼유저와 연결된 BusinessUser를 가져오거나 생성합니다.
        host, created = BusinessUser.objects.get_or_create(user=superuser)

        if created:
            # 새로 생성된 경우, 필요한 추가 정보를 설정합니다.
            host.business_name = "Default Business"
            host.business_registration_number = "000-00-00000"
            host.save()

        # Accommodation 객체를 생성합니다.
        accommodation = serializer.save(host=host)

        # AccommodationType 생성
        accommodation_type_data = self.request.data.get("accommodation_type", {})
        AccommodationType.objects.create(accommodation=accommodation, **accommodation_type_data)

        # GPS_Info 생성
        gps_info_data = self.request.data.get("gps_info", {})
        if not gps_info_data:
            GPS_Info.objects.create(
                accommodation=accommodation,
                location=Point(126.9780, 37.5665),  # 경도, 위도 순서 (서울 좌표)
                city="Default City",
                states="Default State",
                road_name="Default Road",
                address="Default Address",
            )
        else:
            GPS_Info.objects.create(accommodation=accommodation, **gps_info_data)

        # Accommodation_Image 생성
        images_data = self.request.data.get("images", [])
        for image_data in images_data:
            Accommodation_Image.objects.create(accommodation=accommodation, **image_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AccommodationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]


class AccommodationTypeListCreateView(generics.ListCreateAPIView):
    queryset = AccommodationType.objects.all()
    serializer_class = AccommodationTypeSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]


class AccommodationTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccommodationType.objects.all()
    serializer_class = AccommodationTypeSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]


class AccommodationTypeCustomCreateView(APIView):
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def post(self, request):
        serializer = AccommodationTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_customized=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccommodationImageListCreateView(generics.ListCreateAPIView):
    queryset = Accommodation_Image.objects.all()
    serializer_class = AccommodationImageSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]


class AccommodationImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Accommodation_Image.objects.all()
    serializer_class = AccommodationImageSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]


class GPSInfoRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = GPS_Info.objects.all()
    serializer_class = GPSInfoSerializer
    permission_classes = [AllowAny]  # [IsAuthenticated]

    def get_object(self):
        accommodation_id = self.kwargs.get("accommodation_id")
        return get_object_or_404(GPS_Info, accommodation_id=accommodation_id)
