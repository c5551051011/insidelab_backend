# 🚀 Railway 배포 가이드

Railway에서 InsideLab Backend를 dev/prod 환경으로 분리해서 배포하는 방법입니다.

## 📋 배포 전 준비사항

### 1. Git 브랜치 구조
```
main   ← Production 배포용
dev    ← Development 배포용
```

### 2. 필요한 파일들
- ✅ `railway.toml` - Railway 설정 파일
- ✅ `Procfile` - 애플리케이션 시작 명령어
- ✅ `requirements.txt` - Python 패키지 목록
- ✅ `.gitignore` - 환경 변수 파일 보안 제외
- ⚠️ **중요**: 환경 변수는 Railway 대시보드에서 직접 설정 (git에 올리면 안됨!)

## 🛠️ Railway 설정 단계

### 1단계: Railway 프로젝트 생성

1. **Railway 대시보드**에 로그인
2. **"New Project"** 클릭
3. **"Deploy from GitHub repo"** 선택
4. 저장소 선택: `insidelab/backend`

### 2단계: Development 서비스 설정

1. **첫 번째 서비스 생성 (Development)**
   ```
   Service Name: insidelab-backend-dev
   Source: GitHub Repository
   Branch: dev
   ```

2. **Environment Variables 설정**
   ```bash
   # 필수 환경 변수
   DJANGO_ENVIRONMENT=development
   SECRET_KEY=your-dev-secret-key
   DEBUG=true

   # Development Database
   DB_NAME=postgres
   DB_USER=postgres.aetnyvpjauczqlkihpyc
   DB_PASSWORD=DLStkdlemfoq25!@#
   DB_HOST=aws-0-ap-northeast-2.pooler.supabase.com
   DB_PORT=6543

   # Email
   RESEND_API_KEY=re_9Vcn67GY_EkVga5b5qEvJfScy4hrNs6LQ
   DEFAULT_FROM_EMAIL=InsideLab Dev <dev@insidelab.io>

   # Site
   SITE_DOMAIN=your-dev-domain.up.railway.app
   FRONTEND_URL=https://your-frontend-dev-url.com

   # Railway 환경 표시
   RAILWAY_ENVIRONMENT=development
   ```

### 3단계: Production 서비스 설정

1. **두 번째 서비스 생성 (Production)**
   ```
   Service Name: insidelab-backend-prod
   Source: GitHub Repository
   Branch: main
   ```

2. **Environment Variables 설정**
   ```bash
   # 필수 환경 변수
   DJANGO_ENVIRONMENT=production
   SECRET_KEY=your-production-secret-key
   DEBUG=false

   # Production Database
   PROD_DB_NAME=postgres
   PROD_DB_USER=postgres.zwztxgsxjoutvtwugtrq
   PROD_DB_PASSWORD=DLStkdlemfoq25!@#
   PROD_DB_HOST=aws-1-ap-northeast-2.pooler.supabase.com
   PROD_DB_PORT=6543

   # Email
   RESEND_API_KEY=re_9Vcn67GY_EkVga5b5qEvJfScy4hrNs6LQ
   DEFAULT_FROM_EMAIL=InsideLab <noreply@insidelab.io>

   # Site
   SITE_DOMAIN=insidelab.io
   PRODUCTION_DOMAIN=insidelab.io
   FRONTEND_URL=https://insidelab.io

   # Railway 환경 표시
   RAILWAY_ENVIRONMENT=production
   ```

### 4단계: Redis 서비스 추가 (선택사항)

1. **Redis 서비스 생성**
   ```
   Service Type: Redis
   Service Name: insidelab-redis
   ```

2. **Redis 연결 설정**
   - Development 서비스에서:
     ```bash
     REDIS_URL=redis://redis.railway.internal:6379
     ```
   - Production 서비스에서:
     ```bash
     REDIS_URL=redis://redis.railway.internal:6379
     ```

## 🔄 배포 프로세스

### Development 배포
```bash
# dev 브랜치에 push하면 자동 배포
git checkout dev
git add .
git commit -m "Development changes"
git push origin dev
```

### Production 배포
```bash
# main 브랜치에 merge하면 자동 배포
git checkout main
git merge dev
git push origin main
```

## 🔍 배포 확인

### Health Check 엔드포인트
```
Development: https://your-dev-domain.up.railway.app/api/v1/health/
Production: https://your-prod-domain.up.railway.app/api/v1/health/
```

응답 예시:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

### API 문서 확인
```
Development: https://your-dev-domain.up.railway.app/swagger/
Production: https://your-prod-domain.up.railway.app/swagger/
```

## 📊 환경별 특징

| 항목 | Development | Production |
|------|-------------|-----------|
| **브랜치** | `dev` | `main` |
| **DEBUG** | `True` | `False` |
| **데이터베이스** | `postgres.aetnyvpjauczqlkihpyc` | `postgres.zwztxgsxjoutvtwugtrq` |
| **도메인** | `*.up.railway.app` | `insidelab.io` |
| **CORS** | 모든 origin 허용 | 제한된 origin만 허용 |
| **캐시** | Redis (선택사항) | Redis + 최적화된 timeout |
| **로깅** | 상세 로깅 | 최소 로깅 |

## 🚨 트러블슈팅

### 1. 배포 실패 시
```bash
# Railway 로그 확인
railway logs
```

### 2. 데이터베이스 연결 실패
- 환경 변수 확인
- Supabase 네트워크 설정 확인
- 데이터베이스 비밀번호 확인

### 3. 마이그레이션 문제
```bash
# Railway 콘솔에서 수동 마이그레이션
railway run python manage.py migrate
```

### 4. Static 파일 문제
```bash
# Static 파일 수집
railway run python manage.py collectstatic --noinput
```

## 🔐 보안 설정

### 환경 변수 보안
- ✅ SECRET_KEY는 환경별로 다르게 설정
- ✅ 데이터베이스 비밀번호는 Railway Secrets에 저장
- ✅ API 키들은 환경 변수로만 관리

### 네트워크 보안
- ✅ Production CORS 정책 제한
- ✅ HTTPS 강제 적용
- ✅ 보안 헤더 설정

## 📝 주요 명령어

### 로컬 개발
```bash
# Development 환경으로 실행
cp .env.development .env
python manage.py runserver

# Production 환경으로 테스트
cp .env.production .env
DJANGO_ENVIRONMENT=production python manage.py runserver
```

### Railway CLI 사용
```bash
# Railway 설치
npm install -g @railway/cli

# Railway 로그인
railway login

# 환경 변수 설정
railway variables set DJANGO_ENVIRONMENT=production

# 배포 상태 확인
railway status
```

---

**🎯 다음 단계:**
1. **모니터링 설정**: Sentry, DataDog 등
2. **백업 전략**: 데이터베이스 자동 백업
3. **CI/CD 파이프라인**: GitHub Actions 연동
4. **도메인 연결**: 커스텀 도메인 설정