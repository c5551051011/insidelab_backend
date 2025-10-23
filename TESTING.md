# InsideLab Backend - 테스트 가이드

이 문서는 InsideLab 백엔드 프로젝트의 테스트 코드 실행 방법을 안내합니다.

## 테스트 구조

프로젝트의 테스트는 각 앱별로 구성되어 있습니다:

```
apps/
├── authentication/
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       └── test_views.py
├── universities/
│   └── tests/
│       ├── __init__.py
│       └── test_models.py
├── labs/
│   └── tests/
│       ├── __init__.py
│       └── test_models.py
└── reviews/
    └── tests/
        ├── __init__.py
        └── test_models.py
```

## 테스트 실행 방법

### 0. 빠른 시작 (권장)

테스트 실행 스크립트 사용:
```bash
# 전체 테스트 실행
./run_tests.sh

# 특정 앱만 테스트
./run_tests.sh auth           # Authentication 앱
./run_tests.sh universities   # Universities 앱
./run_tests.sh labs           # Labs 앱
./run_tests.sh reviews        # Reviews 앱

# 모델 테스트만 실행
./run_tests.sh models

# 뷰/API 테스트만 실행
./run_tests.sh views
```

### 1. Django 기본 테스트 러너 사용

전체 테스트 실행:
```bash
DJANGO_SETTINGS_MODULE=insidelab.settings.test python manage.py test
```

특정 앱의 테스트만 실행:
```bash
DJANGO_SETTINGS_MODULE=insidelab.settings.test python manage.py test apps.authentication
DJANGO_SETTINGS_MODULE=insidelab.settings.test python manage.py test apps.universities
DJANGO_SETTINGS_MODULE=insidelab.settings.test python manage.py test apps.labs
DJANGO_SETTINGS_MODULE=insidelab.settings.test python manage.py test apps.reviews
```

특정 테스트 클래스만 실행:
```bash
python manage.py test apps.authentication.tests.test_models.UserModelTest
```

특정 테스트 메서드만 실행:
```bash
python manage.py test apps.authentication.tests.test_models.UserModelTest.test_create_user_with_email
```

상세한 출력과 함께 실행:
```bash
python manage.py test --verbosity=2
```

### 2. Pytest 사용 (선택사항)

pytest를 사용하려면 먼저 설치:
```bash
pip install pytest pytest-django
```

전체 테스트 실행:
```bash
pytest
```

특정 앱의 테스트만 실행:
```bash
pytest apps/authentication/tests/
pytest apps/universities/tests/
pytest apps/labs/tests/
pytest apps/reviews/tests/
```

특정 테스트 파일만 실행:
```bash
pytest apps/authentication/tests/test_models.py
```

특정 테스트 클래스만 실행:
```bash
pytest apps/authentication/tests/test_models.py::UserModelTest
```

특정 테스트 메서드만 실행:
```bash
pytest apps/authentication/tests/test_models.py::UserModelTest::test_create_user_with_email
```

커버리지와 함께 실행:
```bash
pip install pytest-cov
pytest --cov=apps --cov-report=html
```

## 테스트 커버리지

각 앱별 테스트 커버리지:

### Authentication 앱
- **Models**: User, UserLabInterest
- **Views**: 회원가입, 로그인, 프로필 관리, Google 인증, 피드백 제출

### Universities 앱
- **Models**: University, Department, UniversityDepartment, ResearchGroup, Professor, UniversityEmailDomain

### Labs 앱
- **Models**: Lab, ResearchTopic, Publication, RecruitmentStatus, LabCategoryAverage

### Reviews 앱
- **Models**: RatingCategory, Review, ReviewRating, ReviewHelpful

## 테스트 데이터베이스

테스트는 자동으로 임시 데이터베이스를 생성하고 사용합니다. 테스트 완료 후 자동으로 삭제됩니다.

## 주의사항

1. **이메일 발송 테스트**: 실제 이메일이 발송되지 않도록 settings에서 EMAIL_BACKEND를 테스트용으로 설정해야 합니다.

2. **외부 서비스 의존성**: 일부 테스트는 외부 서비스(이메일 발송 등)에 의존할 수 있으며, 해당 서비스가 설정되지 않은 경우 실패할 수 있습니다.

3. **인증 테스트**: API 인증이 필요한 테스트는 `force_authenticate()`를 사용하여 인증을 우회합니다.

## 테스트 작성 가이드

새로운 테스트를 작성할 때는 다음 구조를 따르세요:

```python
from django.test import TestCase
from rest_framework.test import APITestCase

class MyModelTest(TestCase):
    """Test cases for MyModel"""

    def setUp(self):
        """Set up test data"""
        # 테스트에 필요한 데이터 생성
        pass

    def test_something(self):
        """Test description"""
        # 테스트 로직
        self.assertEqual(expected, actual)

class MyAPITest(APITestCase):
    """Test cases for MyAPI"""

    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        # 테스트 데이터 생성
        pass

    def test_api_endpoint(self):
        """Test API endpoint"""
        response = self.client.get('/api/endpoint/')
        self.assertEqual(response.status_code, 200)
```

## 지속적 통합 (CI)

GitHub Actions 또는 다른 CI/CD 도구에서 테스트를 자동으로 실행하려면:

```yaml
- name: Run tests
  run: |
    python manage.py test --verbosity=2
```

## 문제 해결

### 테스트 데이터베이스 관련 오류
```bash
python manage.py test --keepdb  # 테스트 DB 재사용
```

### 특정 테스트만 실패하는 경우
```bash
python manage.py test <app_name> --failfast  # 첫 실패에서 중단
```

### 병렬 실행
```bash
python manage.py test --parallel  # 여러 프로세스로 병렬 실행
```

## 테스트 결과 예시

```
Found 47 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...............................................
----------------------------------------------------------------------
Ran 47 tests in 3.245s

OK
Destroying test database for alias 'default'...
```

## 추가 리소스

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Pytest Django Plugin](https://pytest-django.readthedocs.io/)
