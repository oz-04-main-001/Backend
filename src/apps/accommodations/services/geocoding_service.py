import json
import requests

from apps.common.constants.kakao_constants import KAKAO_SEARCH_URL
from apps.common.util.redis_client import redis_client
from config.settings import KAKAO_REST_API_KEY, NAVER_REST_API_KEY, NAVER_REST_API_SECRET


class GeocodingService:

    def search_accommodations_and_images(self, latitude, longitude, radius=5000, keyword="숙소") -> dict:
        """카카오 API로 숙소 정보를 조회하고, 네이버 API로 각 숙소 이미지 추가"""
        accommodations = self._search_accommodations_with_cache(latitude, longitude, radius, keyword)

        for accommodation in accommodations:
            place_name = accommodation.get("place_name")
            accommodation["image_url"] = self._get_image_with_cache(place_name)

        return accommodations

    def _search_accommodations_with_cache(self, latitude, longitude, radius, keyword) -> list:
        """카카오 API를 통해 숙소 정보 검색, 캐시가 있으면 캐시 사용"""
        cache_key = f"kakao:accommodations:{latitude}:{longitude}:{radius}:{keyword}"

        cached_data = redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        url = KAKAO_SEARCH_URL
        headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
        params = {
            "x": latitude,  # 경도
            "y": longitude,  # 위도
            "radius": radius,  # 검색 반경 (미터 단위)
            "query": keyword,  # 검색 키워드
            "category_group_code": "AD5",  # 숙박 시설 코드 (AD5)
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            places = data.get("documents", [])

            # 데이터 캐싱 (TTL: 30일)
            redis_client.setex(cache_key, 2592000, json.dumps(places))
            return places
        else:
            return []

    def _get_image_with_cache(self, accommodation_name) -> str:
        """네이버 API를 통해 숙소 이미지 검색, 캐시가 있으면 캐시 사용"""
        cache_key = f"naver:image:{accommodation_name}"

        cached_image_url = redis_client.get(cache_key)
        if cached_image_url:
            return cached_image_url.decode("utf-8")

        client_id = NAVER_REST_API_KEY
        client_secret = NAVER_REST_API_SECRET
        url = "https://openapi.naver.com/v1/search/image"
        headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        params = {
            "query": accommodation_name,
            "display": 1,
            "sort": "sim",
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()
            if result["items"]:
                image_url = result["items"][0]["link"]

                redis_client.setex(cache_key, 2592000, image_url)
                return image_url
            else:
                return None
        else:
            return f"Error: {response.status_code}"
