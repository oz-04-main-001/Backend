import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# StreamHandler가 중복 추가되지 않도록 설정
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, APIException):
            error_messages = []
            for field_errors in response.data.values():
                if isinstance(field_errors, list):
                    error_messages.extend([str(error) for error in field_errors])
                else:
                    error_messages.append(str(field_errors))

            response.data = {"code": response.status_code, "errors": " ".join(error_messages)}
    else:
        # 예외 로그 기록 (중복 핸들러 추가 방지)
        logger.error("An unexpected error occurred", exc_info=exc)

        # 기본 응답 생성
        response = Response(
            {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "errors": "An unexpected error occurred.",
                "details": str(exc),  # 예외의 상세 내용 포함
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
