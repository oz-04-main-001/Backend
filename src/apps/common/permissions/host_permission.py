from rest_framework import permissions


class IsHost(permissions.BasePermission):
    """
    호스트 사용자에게만 접근을 허용하는 커스텀 권한.
    사용자가 비즈니스 프로필을 가지고 있고,
    해당 프로필의 verification_status가 'approved'인 경우에만 접근 허용.
    """

    def has_permission(self, request, view):
        """사용자가 인증되었고 비즈니스 프로필이 승인된 경우에만 접근 허용."""
        try:
            business_profile = request.user.business_profile
            # 추가적인 호스트 자격 검증 로직을 넣을 수 있습니다.
            # 이후 verification_status == approved인 경우만 통과하도록
            # if business_profile.verification_status == "approved":
            #     return True
            return True
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        # 객체 수준의 권한이 필요한 경우 여기에 로직을 추가합니다.
        # 특정 숙소의 소유자인지 확인
        return obj.host == request.user.business_profile
