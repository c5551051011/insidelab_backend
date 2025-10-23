# GitHub Actions Workflows

이 디렉토리에는 InsideLab 백엔드의 CI/CD 워크플로우가 포함되어 있습니다.

## 워크플로우 목록

### 1. `tests.yml` - 기본 테스트
간단한 테스트 실행 워크플로우

**실행 시점**:
- `main`, `develop` 브랜치에 push
- Pull Request 생성 시

**작업**:
- Python 3.10 환경 설정
- 의존성 설치
- 모든 모델 테스트 실행
- Flake8 린팅

### 2. `django-ci.yml` - 전체 CI/CD 파이프라인
상세한 CI/CD 파이프라인

**실행 시점**:
- `main`, `develop` 브랜치에 push
- Pull Request 생성 시

**작업**:

#### Test Job
- Python 3.10, 3.11에서 테스트 실행
- 마이그레이션 체크
- 앱별 개별 테스트 실행
- 테스트 요약 생성

#### Lint Job
- Flake8으로 코드 품질 체크
- Pylint 정적 분석

#### Security Job
- Safety로 의존성 취약점 검사
- Bandit으로 보안 이슈 스캔

#### Coverage Job (PR only)
- 테스트 커버리지 측정
- HTML 리포트 생성 및 업로드

#### Build Status Job
- 모든 체크 결과 종합

## 배지 추가하기

README.md에 다음 배지를 추가하세요:

```markdown
![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Django%20Tests/badge.svg)
![CI/CD](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Django%20CI%2FCD/badge.svg)
```

## 로컬에서 테스트

GitHub Actions와 동일한 환경에서 로컬 테스트:

```bash
# 전체 테스트
export DJANGO_SETTINGS_MODULE=insidelab.settings.test
python manage.py test apps.authentication.tests.test_models apps.universities.tests apps.labs.tests apps.reviews.tests --verbosity=2

# 린팅
flake8 apps/ insidelab/ --exclude=migrations,__pycache__,venv

# 보안 체크
safety check
bandit -r apps/ insidelab/
```

## 문제 해결

### 테스트 실패 시
1. 로컬에서 먼저 테스트 실행
2. `DJANGO_SETTINGS_MODULE=insidelab.settings.test` 환경변수 확인
3. 의존성 버전 확인 (`requirements.txt`)

### 워크플로우 수정 시
1. YAML 문법 검증
2. 로컬에서 명령어 테스트
3. Draft PR로 먼저 확인

## 추가 정보

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Django 테스트 문서](https://docs.djangoproject.com/en/stable/topics/testing/)
