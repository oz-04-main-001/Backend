import requests

from apps.common.constants.kakao_constants import KAKAO_SEARCH_URL
from config.settings import KAKAO_REST_API_KEY


class GeocodingService:

    @staticmethod
    def search_accommodations(latitude, longitude, radius=5000, keyword="숙소"):
        url = KAKAO_SEARCH_URL

        headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}

        params = {
            "x": longitude,  # 경도
            "y": latitude,  # 위도
            "radius": radius,  # 검색 반경 (미터 단위)
            "query": keyword,  # 검색 키워드
            "category_group_code": "AD5",  # 숙박 시설 코드 (AD5)
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            places = data.get("documents", [])

            print(places)
            for place in places:
                name = place.get("place_name")
                address = place.get("road_address_name", place.get("address_name"))
                distance = place.get("distance")
                print(f"숙소 이름: {name}, 주소: {address}, 거리: {distance}m")

            return places
        else:
            print(f"API 요청 실패: {response.status_code}")
            return None
