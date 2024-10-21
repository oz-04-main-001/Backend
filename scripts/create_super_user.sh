#!/usr/bin/env bash
set -eo pipefail

docker-compose exec django_gunicorn bash -c "source ~/.bashrc && python src/manage.py createsuperuser"