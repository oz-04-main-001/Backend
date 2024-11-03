import re

from django.contrib.auth import authenticate, get_user_model
from django.core.validators import validate_email
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.auth.services.auth_service import UserAuthService
from apps.common.util.email.services.otp_service import OTPService
from apps.users.models import BusinessUser

User = get_user_model()


class HostRegisterSerializer(serializers.ModelSerializer[User]):  # type: ignore

    class Meta:
        model = BusinessUser
        fields = [
            "user",
            "business_number",
            "business_document",
            "business_email",
            "business_phonenumber",
            "business_address",
            "verified_at",
            "verification_status",
        ]
        read_only_fields = ["user", "verified_at", "verification_status"]
        extra_kwargs = {
            "business_number": {"required": True},
            "business_document": {"required": True},
            "business_email": {"required": True},
            "business_phonenumber": {"required": True},
        }

    def validate_business_number(self, value):
        # 한국 사업자등록번호 형식 검증 (XXX-XX-XXXXX)
        pattern = re.compile(r"^\d{3}-\d{2}-\d{5}$")
        if not pattern.match(value):
            raise serializers.ValidationError("올바른 사업자등록번호 형식이 아닙니다.")
        return value

    def validate_business_email(self, value):
        # 이메일 형식 검증
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("올바른 이메일 형식이 아닙니다.")
        return value

    def validate_business_phonenumber(self, value):
        # 전화번호 형식 검증
        pattern = re.compile(r"^(02|0\d{2})-?\d{3,4}-?\d{4}$")
        if not pattern.match(value):
            raise serializers.ValidationError("올바른 전화번호 형식이 아닙니다.")
        return value

    def validate_business_document(self, value):
        # 파일 크기 제한
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError("파일 크기는 5MB를 초과할 수 없습니다.")

        # 파일 형식 제한
        allowed_types = ["application/pdf", "image/jpeg", "image/png"]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("허용되지 않는 파일 형식입니다.")

        return value
