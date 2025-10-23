# InsideLab Backend

[![Django Tests](https://github.com/c5551051011/insidelab_backend/workflows/Django%20Tests/badge.svg)](https://github.com/c5551051011/insidelab_backend/actions/workflows/tests.yml)
[![Django CI/CD](https://github.com/c5551051011/insidelab_backend/workflows/Django%20CI%2FCD/badge.svg)](https://github.com/c5551051011/insidelab_backend/actions/workflows/django-ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 4.2+](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)

InsideLab 프로젝트의 Django REST Framework 기반 백엔드 API 서버입니다.

## 🚀 주요 기능

- **인증 시스템**: JWT 기반 사용자 인증, Google OAuth 지원
- **대학 관리**: 대학, 학과, 교수, 연구 그룹 정보 관리
- **연구실 정보**: 연구실 상세 정보, 논문, 모집 현황
- **리뷰 시스템**: 다차원 평가 카테고리 기반 연구실 리뷰
- **이메일 검증**: 대학 이메일 도메인 기반 인증

## 📊 테스트 현황

- **총 테스트**: 55개
- **통과율**: 100% ✅
- **실행 시간**: ~0.26초

자세한 내용은 [TESTING.md](TESTING.md)를 참고하세요.

## 🛠 기술 스택

- **Framework**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development/Test)
- **Cache**: Redis
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Email**: Resend API
- **Deployment**: Railway

## 📦 설치 및 실행

### 요구사항

- Python 3.10+
- PostgreSQL (또는 SQLite for development)
- Redis (선택사항, 캐싱용)

### 설치

```bash
# 저장소 클론
git clone https://github.com/c5551051011/insidelab_backend.git
cd insidelab_backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 환경변수 설정

# 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
```

## 🧪 테스트

### 빠른 시작

```bash
# 전체 테스트 실행
./run_tests.sh

# 특정 앱만 테스트
./run_tests.sh auth
./run_tests.sh universities
./run_tests.sh labs
./run_tests.sh reviews
```

### 수동 실행

```bash
# 환경변수 설정
export DJANGO_SETTINGS_MODULE=insidelab.settings.test

# 모든 모델 테스트
python manage.py test apps.authentication.tests.test_models \
                      apps.universities.tests \
                      apps.labs.tests \
                      apps.reviews.tests --verbosity=2

# 특정 앱 테스트
python manage.py test apps.authentication.tests --verbosity=2
```

자세한 테스트 가이드는 [TESTING.md](TESTING.md)를 참고하세요.

## 📁 프로젝트 구조

```
insidelab_backend/
├── apps/
│   ├── authentication/    # 사용자 인증 및 관리
│   │   └── tests/        # 인증 테스트
│   ├── universities/      # 대학 정보 관리
│   │   └── tests/        # 대학 테스트
│   ├── labs/             # 연구실 정보
│   │   └── tests/        # 연구실 테스트
│   ├── reviews/          # 리뷰 시스템
│   │   └── tests/        # 리뷰 테스트
│   └── publications/     # 논문 관리
├── insidelab/
│   ├── settings/         # 환경별 설정
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py       # 테스트 설정
│   └── urls.py           # URL 라우팅
├── .github/
│   └── workflows/        # GitHub Actions CI/CD
│       ├── tests.yml
│       └── django-ci.yml
├── requirements.txt      # Python 의존성
├── manage.py
└── README.md
```

## 🔄 CI/CD

GitHub Actions를 통한 자동화된 테스트 및 배포:

- **테스트**: 모든 Push 및 PR에서 자동 실행
- **린팅**: Flake8, Pylint를 통한 코드 품질 검사
- **보안**: Safety, Bandit을 통한 보안 스캔
- **커버리지**: PR에서 테스트 커버리지 리포트 생성

자세한 내용은 [.github/workflows/README.md](.github/workflows/README.md)를 참고하세요.

## 📖 API 문서

서버 실행 후 다음 주소에서 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 코드 스타일

- PEP 8 준수
- Flake8 린팅 통과 필수
- 모든 새로운 기능에 대한 테스트 작성 필수

## 📄 라이선스

This project is licensed under the MIT License.

## 📞 문의

- Repository: [https://github.com/c5551051011/insidelab_backend](https://github.com/c5551051011/insidelab_backend)
- Issues: [https://github.com/c5551051011/insidelab_backend/issues](https://github.com/c5551051011/insidelab_backend/issues)

## 📚 추가 문서

- [테스트 가이드](TESTING.md) - 상세한 테스트 실행 방법
- [테스트 요약](TEST_SUMMARY.md) - 작성된 테스트 코드 개요
- [테스트 결과](TEST_RESULTS_FINAL.md) - 최종 테스트 결과 및 픽스처 개선
- [로컬 개발 가이드](LOCAL_DEVELOPMENT.md) - 로컬 환경 설정
- [배포 가이드](DEPLOYMENT.md) - 프로덕션 배포 방법

---

**Generated with** [Claude Code](https://claude.ai/code) **via** [Happy](https://happy.engineering)
