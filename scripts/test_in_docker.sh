#!/usr/bin/env bash
set -eo pipefail

# Docker 컨테이너 내부에서 pyenv 활성화 후, Django 테스트 실행
docker-compose exec django_gunicorn bash -c "
  source ~/.bashrc && \
  pyenv activate django-main && \
  python src/manage.py test --pattern="tests_*.py"
"