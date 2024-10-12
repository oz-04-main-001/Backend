# Backend 프로젝트

이 프로젝트는 Django와 PostgreSQL을 사용하는 백엔드 애플리케이션입니다. Docker 및 Docker Compose를 통해 쉽게 실행할 수 있습니다.

## 요구 사항

- [Docker](https://www.docker.com/) 및 [Docker Compose](https://docs.docker.com/compose/install/) 설치

## 실행 방법

### 1. 프로젝트 클론

먼저 GitHub에서 프로젝트를 클론받습니다:

```bash
git clone https://github.com/oz-04-main-001/Backend.git .
```

### 2. 애플리케이션 실행

Docker Compose 명령어로 애플리케이션을 빌드하고 실행합니다:


```bash
docker-compose up --build
```

### 3. Local에서 작업

poetry를 이용해 가상환경 및 의존성을 설치합니다

```bash
poetry install
poetry shell
```