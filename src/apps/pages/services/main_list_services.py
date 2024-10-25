from rest_framework.pagination import PageNumberPagination


class MainListPagination(PageNumberPagination):
    # 한번에 50 개의 데이터를 보내도록 설정
    page_size = 48
