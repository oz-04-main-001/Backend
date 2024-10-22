from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accommodations.models import Accommodation
from apps.accommodations.serializers.accommodation_serializer import (
    AccommodationSerializer,
)


@extend_schema(tags=["Host"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def accommodation_list(request):
    accommodations = Accommodation.objects.filter(host=request.user, is_active=True)
    serializer = AccommodationSerializer(accommodations, many=True)
    return Response(serializer.data)


@extend_schema(tags=["Host"])
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accommodation_create(request):
    serializer = AccommodationSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save(host=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Host"])
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def accommodation_detail(request, pk):
    try:
        accommodation = Accommodation.objects.get(pk=pk, host=request.user)
    except Accommodation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = AccommodationSerializer(accommodation)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = AccommodationSerializer(accommodation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        accommodation.is_active = False
        accommodation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Host"])
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accommodation_activate(request, pk):
    try:
        accommodation = Accommodation.objects.get(pk=pk, host=request.user)
    except Accommodation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    accommodation.is_active = True
    accommodation.save()
    return Response({"status": "accommodation activated"})
