from django.db.models import Q


def email_or_phone_condition(email: str, phone_number: str) -> Q:
    """
    이메일 또는 전화번호 중복 확인을 위한 조건을 반환
    """
    return Q(email=email) | Q(phone_number=phone_number)
