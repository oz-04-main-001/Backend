#!/bin/bash

# 가상 환경 활성화
source ~/.bashrc
pyenv activate django-main

# 프로젝트 디렉토리로 이동
cd src

# 데이터베이스 마이그레이션
echo "Applying database migrations..."
poetry run python manage.py migrate --no-input

# 슈퍼유저 생성
echo "Creating superuser..."
poetry run python manage.py shell << END
from django.contrib.auth import get_user_model

User = get_user_model()

# 이미 생성된 슈퍼유저가 없는 경우에만 생성
if not User.objects.filter(email='admin@naver.com').exists():
    user = User.objects.create_superuser(
        email='admin@naver.com',
        password='12345678',  # 원하는 비밀번호로 설정
        first_name='Hong',
        last_name='Hong',
        phone_number='010-1111-2222',
        birth_date='2024-10-17'
    )
    user.save()
END

# 정적 파일 수집
echo "Collecting static files..."
poetry run python manage.py collectstatic --no-input

# GDAL 및 GEOS 설정 및 버전 확인
echo "GDAL_LIBRARY_PATH is set to: $GDAL_LIBRARY_PATH"
echo "GEOS_LIBRARY_PATH is set to: $GEOS_LIBRARY_PATH"

# GDAL 버전 정보 출력
echo "Checking GDAL version..."
gdalinfo --version || echo "GDAL is not installed or GDAL_LIBRARY_PATH is incorrect."

# GEOS 버전 정보 출력
echo "Checking GEOS version..."
geos-config --version || echo "GEOS is not installed or GEOS_LIBRARY_PATH is incorrect."

# GDAL 라이브러리 경로 찾기
echo "Finding libgdal.so..."
find / -name "libgdal.so" || echo "libgdal.so not found."

# GEOS 라이브러리 경로 찾기
echo "Finding libgeos_c.so..."
find / -name "libgeos_c.so" || echo "libgeos_c.so not found."


# Gunicorn 실행
echo "Starting Gunicorn..."
exec poetry run gunicorn config.wsgi:application --bind 0.0.0.0:8000
