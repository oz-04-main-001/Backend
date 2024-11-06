# 숙박등록, 예약 서비스 STAYNEST

메인 레포 : https://github.com/oz-04-main-001 <br/>

Test ID : admin@naver.com, guest@naver.com, host@naver.com  <br/>
Test PW : 12345678 <br/>

## 📖 프로젝트 소개

>숙박등록, 예약 서비스 STAYNEST
Staynest는 호스트가 손쉽게 숙소와 객실을 등록하고, 유저가 다양한 숙소 옵션을 찾아 예약할 수 있는 플랫폼입니다. 에어비앤비나 아고다와 유사하게, 사용자는 다양한 위치와 스타일의 숙소를 탐색하고 원하는 일정을 선택해 간편하게 예약할 수 있습니다. 또한, 예약 취소 기능을 통해 유연한 일정 조율이 가능합니다.


---
## :link: 배포 링크

> ### [⛪ STAYNEST](https://staynest.site/)

---
## 🗣️ 프로젝트 발표 영상 & 발표 문서

> ### 🗓️ 2024.10-10 - 2024.11.06
> ### [📺 발표 영상 예시]()
> ### [📑 발표 문서 예시]()

---

## 🧰 사용 스택


### :wrench: System Architecture

<img src="https://media.discordapp.net/attachments/1296038799155007528/1303487480347234405/Artboard_1.png?ex=672beed0&is=672a9d50&hm=0ab97a449aeb76ee99c1359f7d7938a9a45c6a2b9e511c4041276776d1ce15d5&=&format=webp&quality=lossless&width=1308&height=1046"/>


### BE
<div align=center> 
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white"> 
  <img src="https://img.shields.io/badge/redis-D0271D?style=for-the-badge&logo=redis&logoColor=white">
  <br>

  <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white">
  <img src="https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"> 
  <img src="https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white">
  <br>

  <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white">
  <img src="https://img.shields.io/badge/swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black">
  <img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/postgis-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <br>

  <img src="https://img.shields.io/badge/ec2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white">
  <img src="https://img.shields.io/badge/rds-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white">
  <img src="https://img.shields.io/badge/s3-569A31?style=for-the-badge&logo=amazons3&logoColor=white">
</div>



--- 

## :busts_in_silhouette: 팀 동료



### BE
 ## 팀원 구성

| 김태우(BE)                                                                                      | 정민준(BE)                                                                                     | 송미현(BE)                                                                                      | 이동혁(BE)                                                                               | 가현서(BE)                                                                               |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| <img src ="https://avatars.githubusercontent.com/u/146797468?v=4" width=200> <br /> @taewooD | <img src ="https://avatars.githubusercontent.com/u/174682226?v=4" width=200> <br /> @babbod | <img src ="https://avatars.githubusercontent.com/u/146797468?v=4" width=200> <br /> @mihyeon | <img src ="https://avatars.githubusercontent.com/u/174682226?v=4" width=200> <br /> @dongguri | <img src ="https://avatars.githubusercontent.com/u/146797468?v=4" width=200> <br /> @hyeonseoping | 


## 📑 프로젝트 규칙

### 개발환경

- **Backend**: Django, Gunicorn, Nginx, Docker, Redis, PostGIS (거리 계산)
- **배포환경**: AWS (EC2 + RDS)
- **파일 관리**: AWS S3 (파일 업로드)
- **세션 및 캐시 관리**: Redis
- **DB 관리**: RDS with PostGIS (공간 데이터 활용)
- **버전 및 이슈 관리**: GitHub, GitHub Issues
- **협업 툴**: Discord, Notion

---

### 채택한 기술 스택 및 사용 이유

- **Docker** - 컨테이너 기반 환경
  - **이점**: 애플리케이션과 모든 종속성을 함께 배포하여 이식성과 일관성을 높입니다.
  - **사용 이유**: 구성 요소를 독립적으로 관리하고, 배포 프로세스를 간소화하기 위해 선택했습니다.

- **Django** - 백엔드 프레임워크
  - **이점**: 신속한 개발과 유지보수를 지원하며, 보안과 유효성 검증 기능이 내장되어 있습니다.
  - **사용 이유**: 데이터 중심의 애플리케이션에 적합하여, 예약 사이트 개발에 유용합니다.

- **Gunicorn** - Python WSGI 서버
  - **이점**: 워커 수 조절로 서버 성능을 최적화할 수 있습니다.
  - **사용 이유**: Django 애플리케이션의 성능을 높이고 안정적으로 배포하기 위해 사용했습니다.

- **Nginx** - 리버스 프록시 및 정적 파일 제공
  - **이점**: 높은 처리량을 지원하며, 정적 파일을 효과적으로 캐싱합니다.
  - **사용 이유**: Gunicorn과 함께 사용하여 트래픽 관리와 파일 제공을 최적화했습니다.

- **PostGIS** - 공간 데이터 확장 기능
  - **이점**: 공간 쿼리로 거리 계산이 가능해 위치 기반 서비스 구현에 용이합니다.
  - **사용 이유**: 거리 계산이 필요한 기능을 효과적으로 지원할 수 있습니다.

- **AWS S3** - 파일 스토리지
  - **이점**: 확장 가능하고 안정적인 파일 저장소로, 파일 관리가 수월합니다.
  - **사용 이유**: 이미지 및 파일 업로드 기능을 안정적으로 제공하기 위해 선택했습니다.

- **Redis** - 세션 및 캐시 저장소
  - **이점**: 고속 데이터 저장 및 검색이 가능하여 세션 관리와 캐시 처리에 최적입니다.
  - **사용 이유**: 세션과 캐시 데이터를 빠르게 처리해 애플리케이션 성능을 높이기 위해 도입했습니다.

---

### 브랜치 전략

- **Git-flow 전략**을 적용하여 **main**, **develop**, **feature** 브랜치로 나누어 관리했습니다.
  - **main**: 배포 단계에서 사용하는 안정된 브랜치입니다.
  - **develop**: 통합 및 테스트 단계에서 사용하는 브랜치입니다.
  - **feature**: 각 기능 단위로 독립적으로 개발하기 위해 사용합니다. 기능 개발 후 **develop** 브랜치에 병합하고, 해당 브랜치는 삭제합니다.

main, develop branch로 직접 push하는 경우를 방지하기 위해 rule set을 하여 feature branch로 push 후 develop으로 병합하였습니다.

### Git Convention
> 1. 적절한 커밋 접두사 작성
> 2. 커밋 메시지 내용 작성
> 3. 내용 뒤에 이슈 (#이슈 번호)와 같이 작성하여 이슈 연결

> | 접두사        | 설명                           |
> | ------------- | ------------------------------ |
> | Feat :     | 새로운 기능 구현               |
> | Add :      | 에셋 파일 추가                 |
> | Fix :      | 버그 수정                      |
> | Docs :     | 문서 추가 및 수정              |
> | Style :    | 스타일링 작업                  |
> | Refactor : | 코드 리팩토링 (동작 변경 없음) |
> | Test :     | 테스트                         |
> | Deploy :   | 배포                           |
> | Conf :     | 빌드, 환경 설정                |
> | Chore :    | 기타 작업                      |


### Pull Request
> ### Title
> * 제목은 '[Feat] 홈 페이지 구현'과 같이 작성합니다.

> ### PR Type
  > - [ ] FEAT: 새로운 기능 구현
  > - [ ] ADD : 에셋 파일 추가
  > - [ ] FIX: 버그 수정
  > - [ ] DOCS: 문서 추가 및 수정
  > - [ ] STYLE: 포맷팅 변경
  > - [ ] REFACTOR: 코드 리팩토링
  > - [ ] TEST: 테스트 관련
  > - [ ] DEPLOY: 배포 관련
  > - [ ] CONF: 빌드, 환경 설정
  > - [ ] CHORE: 기타 작업

> ### Description
> * 구체적인 작업 내용을 작성해주세요.
> * 이미지를 별도로 첨부하면 더 좋습니다 👍

> ### Discussion
> * 추후 논의할 점에 대해 작성해주세요.

### Code Convention
>BE
> - 패키지명 전체 소문자
> - 클래스명, 인터페이스명 CamelCase
> - 클래스 이름 명사 사용
> - 상수명 SNAKE_CASE
> - Controller, Service, Dto, Repository, mapper 앞에 접미사로 통일(ex. MemberController)
> - service 계층 메서드명 get, post, patch, delete로 CRUD 통일(ex. createMember) 
> - Test 클래스는 접미사로 Test 사용(ex. memberFindTest)



### Communication Rules
> - Discord 활용 
> - 정기 회의


## :clipboard: Documents
> [📜 API 명세서](https://www.notion.so/API-EndPoint-11902f7b1a0580bfa270c1f314ffc322)
> 
> [📜 요구사항 정의서](https://celestial-rhubarb-171.notion.site/121ecf98375b80dda13bf5770b4403ef)
> 
> [📜 ERD](https://www.erdcloud.com/d/czuCKBCv2gnCiLtfr)
> 
> [📜 테이블 명세서](https://docs.google.com/spreadsheets/d/1lCI18Px3IvPLt7Pw9possLvMv04F18y8XgZbRfCPhzw/edit?gid=0#gid=0)

## 4. 역할분담

### 김태우 (팀장)

- **기능**
  1. **회원가입 / 로그인**
     - JWT 토큰을 발급하여 인증과 인가를 처리했습니다.
  
  2. **지도 서비스**
     - 카카오 맵과 네이버 맵을 활용하여 위치 정보를 제공하고, 지도에 숙박 업소 리스트를 표시합니다.
     - 위치 정보와 숙소 이미지를 함께 가져와서, 데이터베이스의 숙소 정보와 함께 조회 결과로 전달합니다.

  3. **검색 기능**
     - 사용자가 입력한 도/시, 체크인, 체크아웃 날짜, 숙박 인원을 기반으로 예약 가능한 객실이 있는 숙소를 응답으로 전달합니다.
     - 검색 결과에는 카카오 지도에 있는 숙박 업소 리스트를 포함하여 응답합니다.
     - 지도를 통해 숙박 업소의 위치를 시각적으로 확인할 수 있도록 구현했습니다.

  4. **디테일 페이지**
     - 숙소와 객실의 상세 정보를 보여줍니다.
     - 로그인한 유저:
       - 숙소: 객실 디테일 또는 예약하기 페이지로 이동합니다.
       - 객실: 예약하기 페이지로 이동합니다.
     - 비로그인 유저:
       - 숙소: 버튼 클릭 시, 로그인 페이지로 이동합니다.

  5. **마이페이지**
     - 호스트 등록 및 숙소 관리 페이지로 이동하는 기능을 제공합니다.
     - 유저 정보를 렌더링하고, 유저의 숙박 예약 및 이용 정보 리스트를 확인할 수 있습니다.
     - 예약 취소는 이용 전까지 가능하도록 설정했습니다.

  6. **호스트 등록**
     - 일반 유저(guest)가 호스트로 등록할 때 사업자 정보 입력 페이지로 이동하여 관련 정보를 입력할 수 있습니다.

  7. **특정 기간 예약 가능한 숙소 필터링**
     - 특정 기간 동안 예약이 가능한 방이 있는 숙소를 필터링하여 제공합니다.
     - 선택한 체크인 및 체크아웃 날짜에 맞춰 예약 가능한 객실이 있는 숙소만 조회해 응답으로 전달합니다.

---

### 배포

- **배포 환경**:
  - **AWS EC2**를 사용하여 **Docker**로 **Nginx**, **Gunicorn** (Django), **Redis**를 운영 중입니다.
  - **RDS**와 **S3**를 활용하여 데이터베이스 관리 및 파일 스토리지를 설정하였습니다.

    

### 정민준

### 송미현

### 이동혁

### 가현서


### 작업 관리

GitHub Projects와 Issues를 사용하여 진행 상황을 공유했습니다.
데일리스크럼을 진행하며 작업 순서와 방향성에 대한 고민을 나누었습니다.


## 7. 트러블 슈팅

- 김태우
1. **로그인 시 OTP 이메일 스팸 방지 문제**
   - **문제**: 로그인 시 사용자가 OTP 이메일 요청 버튼을 빠르게 두 번 누를 경우 중복 요청이 발생하여, 이메일이 여러 번 전송되는 문제가 있었습니다.
   - **해결**: 첫 번째 요청 시 OTP 정보를 Redis에 저장하고, 이후 동일한 요청이 들어오면 "5분 뒤에 다시 시도해 주세요"라는 메시지를 반환하도록 설정했습니다. 또한, 1분 안에 동일 IP에서 10회 이상 OTP 요청이 발생하면 해당 IP를 차단하여 보안성을 높였습니다.

2. **외부 API 호출 비용 절감을 위한 숙소 데이터 캐싱 문제**
   - **문제**: 지역 및 위치 기반 숙소 리스트를 제공할 때 카카오 및 네이버 API를 자주 호출하면서 외부 API 비용이 증가했습니다.
   - **해결**: Redis에 숙소 데이터를 캐싱하여, 한 번 조회한 데이터는 한 달간 Redis에 저장해 이후에는 캐싱된 데이터를 사용하도록 했습니다. 이를 통해 반복적인 API 호출을 줄이고 비용을 절감할 수 있었습니다.

3. **t2.micro 인스턴스에서의 성능 저하 문제**
   - **문제**: 초기에는 EC2 t2.micro 인스턴스에서 Redis, Nginx, Django(Gunicorn), PostGIS를 모두 Docker 컨테이너로 실행했으나, CPU 크레딧이 소진되면서 성능이 크게 저하되었습니다.
   - **해결**: 성능을 개선하기 위해 PostGIS를 Amazon RDS로 분리하고, EC2 인스턴스를 소형(small) 인스턴스로 업그레이드했으며, 스토리지 볼륨도 확장하여 리소스 문제를 해결했습니다.


## 8. 프로젝트 후기

### 김태우 (팀장)
처음 팀장 역할을 맡아 프로젝트를 이끌어가는 과정에서 많은 부담과 어려움을 느꼈습니다. 하지만, 소통, 역할 분담, 문서화, 프로젝트 세팅부터 배포까지 다양한 역할을 맡으며 이전보다 많이 성장할 수 있었다고 생각합니다.

특히, 기획 단계에서 모든 팀원이 같은 방향을 바라보고 있는지 확실히 하는 것이 중요하다는 점을 깨달았습니다. 이번 프로젝트에서는 각자 기획 의도를 다르게 이해한 부분이 있어 불필요한 작업이 발생하기도 했습니다. 이를 통해 프론트와 백엔드 간의 소통이 얼마나 중요한지 실감하게 되었고, 서로를 배려하며 협력하는 마음가짐이 팀 프로젝트의 성공에 필수적임을 느꼈습니다.

팀장으로서 한층 성장할 수 있었던 좋은 경험이었고, 앞으로도 이번 경험을 바탕으로 더 나은 협업을 이끌어가고 싶습니다.

