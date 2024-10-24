from rest_framework import permissions


class IsHost(permissions.BasePermission):
    """
    호스트 사용자에게만 접근을 허용하는 커스텀 권한.
    사용자가 비즈니스 프로필을 가지고 있고,
    해당 프로필의 verification_status가 'approved'인 경우에만 접근 허용.
    """

    def has_permission(self, request, view):
        """사용자가 인증되었고 비즈니스 프로필이 승인된 경우에만 접근 허용."""

        # 비즈니스 프로필이 있는지 확인
        try:
            business_profile = request.user.business_profile

            # 비즈니스 프로필의 검증 상태 확인
            # if business_profile.verification_status == "approved":

            # 사용자 유형이 'host' 또는 'admin'인 경우만 허용
            if request.user.user_type in ["host", "admin"]:
                return True
        except AttributeError:
            return False  # 비즈니스 프로필이 없는 경우 접근 거부

        return False  # 위 조건을 모두 만족하지 않으면 접근 거부

    def has_object_permission(self, request, view, obj):
        # 객체 수준의 권한이 필요한 경우 여기에 로직을 추가합니다.
        # 특정 숙소의 소유자인지 확인
        return obj.host == request.user.business_profile
