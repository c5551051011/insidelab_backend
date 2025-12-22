# Recruitment Status API 사용 가이드

연구실 모집 현황을 독립적으로 관리할 수 있는 API 가이드입니다.

## 📌 개요

이 API를 사용하면 Lab 전체 정보를 수정하지 않고 모집 현황(PhD, Postdoc, Intern)만 독립적으로 관리할 수 있습니다.

### Base URL
```
/api/v1/labs/recruitment/
```

### 인증
- **읽기(GET)**: 인증 불필요
- **쓰기(POST, PUT, PATCH, DELETE)**: JWT 토큰 인증 필요

```bash
Authorization: Bearer <your_access_token>
```

---

## 🔍 API 엔드포인트

### 1. 모집 현황 목록 조회

모든 연구실의 모집 현황을 조회합니다.

**엔드포인트**
```
GET /api/v1/labs/recruitment/
```

**쿼리 파라미터**
- `recruiting_phd` (boolean): PhD 모집 중인 연구실만 조회
- `recruiting_postdoc` (boolean): Postdoc 모집 중인 연구실만 조회
- `recruiting_intern` (boolean): Intern 모집 중인 연구실만 조회

**예시 요청**
```bash
# 모든 모집 현황 조회
curl -X GET "http://localhost:8000/api/v1/labs/recruitment/"

# PhD 모집 중인 연구실만 조회
curl -X GET "http://localhost:8000/api/v1/labs/recruitment/?recruiting_phd=true"

# Postdoc과 Intern 모집 중인 연구실만 조회
curl -X GET "http://localhost:8000/api/v1/labs/recruitment/?recruiting_postdoc=true&recruiting_intern=true"
```

**응답 예시**
```json
[
  {
    "id": 1,
    "lab_name": "AI Research Lab",
    "is_recruiting_phd": true,
    "is_recruiting_postdoc": false,
    "is_recruiting_intern": true,
    "notes": "Looking for students with ML background",
    "last_updated": "2025-12-22T10:30:00Z"
  },
  {
    "id": 2,
    "lab_name": "Computer Vision Lab",
    "is_recruiting_phd": true,
    "is_recruiting_postdoc": true,
    "is_recruiting_intern": false,
    "notes": "Seeking researchers with deep learning experience",
    "last_updated": "2025-12-21T15:20:00Z"
  }
]
```

---

### 2. 특정 연구실의 모집 현황 조회

특정 연구실의 모집 현황을 상세히 조회합니다.

**엔드포인트**
```
GET /api/v1/labs/recruitment/{lab_id}/
```

**경로 파라미터**
- `lab_id` (integer, required): 연구실 ID

**예시 요청**
```bash
curl -X GET "http://localhost:8000/api/v1/labs/recruitment/1/"
```

**응답 예시**
```json
{
  "id": 1,
  "lab_name": "AI Research Lab",
  "is_recruiting_phd": true,
  "is_recruiting_postdoc": false,
  "is_recruiting_intern": true,
  "notes": "Looking for students with ML background. Strong programming skills required.",
  "last_updated": "2025-12-22T10:30:00Z"
}
```

**에러 응답**
```json
// 404 Not Found
{
  "detail": "Not found."
}
```

---

### 3. 모집 현황 생성

새로운 연구실의 모집 현황을 생성합니다.

**엔드포인트**
```
POST /api/v1/labs/recruitment/
```

**인증 필요**: ✅ Yes

**요청 본문**
```json
{
  "lab": 1,
  "is_recruiting_phd": true,
  "is_recruiting_postdoc": false,
  "is_recruiting_intern": true,
  "notes": "We are looking for passionate PhD students with background in machine learning."
}
```

**예시 요청**
```bash
curl -X POST "http://localhost:8000/api/v1/labs/recruitment/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lab": 1,
    "is_recruiting_phd": true,
    "is_recruiting_postdoc": false,
    "is_recruiting_intern": true,
    "notes": "Looking for students with ML background"
  }'
```

**성공 응답 (201 Created)**
```json
{
  "id": 1,
  "lab_name": "AI Research Lab",
  "is_recruiting_phd": true,
  "is_recruiting_postdoc": false,
  "is_recruiting_intern": true,
  "notes": "Looking for students with ML background",
  "last_updated": "2025-12-22T10:30:00Z"
}
```

**에러 응답**
```json
// 400 Bad Request - lab_id 누락
{
  "error": "lab_id or lab field is required"
}

// 400 Bad Request - 이미 존재
{
  "error": "Recruitment status already exists for this lab. Use PUT or PATCH to update."
}

// 401 Unauthorized - 인증 필요
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 4. 모집 현황 전체 수정

연구실의 모집 현황을 전체적으로 수정합니다. **모든 필드**를 포함해야 합니다.

**엔드포인트**
```
PUT /api/v1/labs/recruitment/{lab_id}/
```

**인증 필요**: ✅ Yes

**경로 파라미터**
- `lab_id` (integer, required): 연구실 ID

**요청 본문**
```json
{
  "is_recruiting_phd": false,
  "is_recruiting_postdoc": true,
  "is_recruiting_intern": true,
  "notes": "Updated recruitment information"
}
```

**예시 요청**
```bash
curl -X PUT "http://localhost:8000/api/v1/labs/recruitment/1/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_recruiting_phd": false,
    "is_recruiting_postdoc": true,
    "is_recruiting_intern": true,
    "notes": "Updated recruitment information"
  }'
```

**성공 응답 (200 OK)**
```json
{
  "id": 1,
  "lab_name": "AI Research Lab",
  "is_recruiting_phd": false,
  "is_recruiting_postdoc": true,
  "is_recruiting_intern": true,
  "notes": "Updated recruitment information",
  "last_updated": "2025-12-22T11:45:00Z"
}
```

---

### 5. 모집 현황 부분 수정 (추천!)

연구실의 모집 현황을 부분적으로 수정합니다. **수정할 필드만** 포함하면 됩니다.

**엔드포인트**
```
PATCH /api/v1/labs/recruitment/{lab_id}/
```

**인증 필요**: ✅ Yes

**경로 파라미터**
- `lab_id` (integer, required): 연구실 ID

**요청 본문** (수정할 필드만 포함)
```json
{
  "is_recruiting_phd": false
}
```

**예시 요청**

```bash
# PhD 모집 중단
curl -X PATCH "http://localhost:8000/api/v1/labs/recruitment/1/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_recruiting_phd": false
  }'

# 여러 필드 동시 수정
curl -X PATCH "http://localhost:8000/api/v1/labs/recruitment/1/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_recruiting_phd": false,
    "is_recruiting_intern": true,
    "notes": "We are now looking for interns instead of PhD students"
  }'

# 노트만 수정
curl -X PATCH "http://localhost:8000/api/v1/labs/recruitment/1/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Application deadline: December 31, 2025"
  }'
```

**성공 응답 (200 OK)**
```json
{
  "id": 1,
  "lab_name": "AI Research Lab",
  "is_recruiting_phd": false,
  "is_recruiting_postdoc": false,
  "is_recruiting_intern": true,
  "notes": "Application deadline: December 31, 2025",
  "last_updated": "2025-12-22T12:00:00Z"
}
```

---

### 6. 모집 현황 삭제

연구실의 모집 현황을 삭제합니다.

**엔드포인트**
```
DELETE /api/v1/labs/recruitment/{lab_id}/
```

**인증 필요**: ✅ Yes

**경로 파라미터**
- `lab_id` (integer, required): 연구실 ID

**예시 요청**
```bash
curl -X DELETE "http://localhost:8000/api/v1/labs/recruitment/1/" \
  -H "Authorization: Bearer <your_token>"
```

**성공 응답 (204 No Content)**
```
(응답 본문 없음)
```

---

## 📊 필드 설명

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `id` | integer | - | 모집 현황 ID (읽기 전용) |
| `lab` | integer | ✅ | 연구실 ID (생성 시에만 필요, write_only) |
| `lab_name` | string | - | 연구실 이름 (읽기 전용) |
| `is_recruiting_phd` | boolean | - | PhD 학생 모집 여부 |
| `is_recruiting_postdoc` | boolean | - | Postdoc 모집 여부 |
| `is_recruiting_intern` | boolean | - | 인턴 모집 여부 |
| `notes` | string | - | 모집 관련 추가 정보 |
| `last_updated` | datetime | - | 마지막 업데이트 시간 (자동 설정) |

---

## 💡 사용 팁

### 1. PATCH vs PUT
- **PATCH 사용 권장**: 특정 필드만 수정하고 싶을 때
- **PUT 사용**: 모든 정보를 새로 덮어쓰고 싶을 때

### 2. 캐시 관리
모집 현황이 변경되면 관련 Lab 캐시가 자동으로 무효화됩니다.

### 3. 필터링 활용
```bash
# PhD와 Postdoc 모두 모집 중인 연구실
GET /api/v1/labs/recruitment/?recruiting_phd=true&recruiting_postdoc=true
```

### 4. lab_id로 직접 접근
Lab 전체 정보를 가져오지 않고 모집 현황만 빠르게 조회/수정 가능합니다.

---

## 🔐 권한

- **AllowAny (읽기)**: 누구나 모집 현황 조회 가능
- **IsAuthenticated (쓰기)**: 로그인한 사용자만 생성/수정/삭제 가능

---

## 🌐 프론트엔드 통합 예시

### React 예시

```javascript
// 모집 현황 조회
const fetchRecruitmentStatus = async (labId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/labs/recruitment/${labId}/`
  );
  return await response.json();
};

// 모집 현황 부분 수정
const updateRecruitmentStatus = async (labId, updates) => {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/labs/recruitment/${labId}/`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(updates)
    }
  );
  return await response.json();
};

// 사용 예시
const handleTogglePhD = async () => {
  await updateRecruitmentStatus(labId, {
    is_recruiting_phd: !currentStatus.is_recruiting_phd
  });
};
```

### Python 예시

```python
import requests

API_BASE_URL = "http://localhost:8000"
ACCESS_TOKEN = "your_access_token"

# 모집 현황 조회
def get_recruitment_status(lab_id):
    url = f"{API_BASE_URL}/api/v1/labs/recruitment/{lab_id}/"
    response = requests.get(url)
    return response.json()

# 모집 현황 수정
def update_recruitment_status(lab_id, updates):
    url = f"{API_BASE_URL}/api/v1/labs/recruitment/{lab_id}/"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.patch(url, json=updates, headers=headers)
    return response.json()

# 사용 예시
status = get_recruitment_status(1)
print(f"Lab: {status['lab_name']}")
print(f"Recruiting PhD: {status['is_recruiting_phd']}")

# PhD 모집 시작
update_recruitment_status(1, {"is_recruiting_phd": True})
```

---

## 📚 Swagger 문서

API를 직접 테스트하려면 Swagger UI를 사용하세요:

```
http://localhost:8000/api/v1/swagger/
```

또는 ReDoc:

```
http://localhost:8000/api/v1/redoc/
```

---

## ❓ FAQ

### Q: Lab 생성 시 자동으로 recruitment_status가 생성되나요?
A: 아니요. 별도로 POST 요청을 통해 생성해야 합니다.

### Q: Lab이 삭제되면 recruitment_status도 삭제되나요?
A: 네, CASCADE 설정으로 자동 삭제됩니다.

### Q: 이미 존재하는 recruitment_status를 POST로 생성하려 하면?
A: 400 에러가 반환되며, PUT 또는 PATCH를 사용하라는 메시지가 표시됩니다.

### Q: 인증 없이 수정하려 하면?
A: 401 Unauthorized 에러가 반환됩니다.

---

## 🎯 실전 시나리오

### 시나리오 1: 모집 상태 토글
```bash
# 현재 상태 확인
GET /api/v1/labs/recruitment/1/

# PhD 모집 토글 (현재 true -> false)
PATCH /api/v1/labs/recruitment/1/
{
  "is_recruiting_phd": false
}
```

### 시나리오 2: 모집 공고 업데이트
```bash
# 새로운 모집 공고 작성
PATCH /api/v1/labs/recruitment/1/
{
  "is_recruiting_phd": true,
  "is_recruiting_intern": true,
  "notes": "Spring 2026 intake now open! Looking for students with strong NLP background. Deadline: Jan 15, 2026"
}
```

### 시나리오 3: 모집 중인 연구실 찾기
```bash
# AI 분야에서 PhD 모집 중인 연구실 찾기
GET /api/v1/labs/recruitment/?recruiting_phd=true

# 결과를 Lab 정보와 함께 활용
# (lab_name 필드 포함되어 있음)
```

---

## 📞 지원

문제가 발생하거나 질문이 있으시면:
- GitHub Issues: [프로젝트 이슈 페이지]
- Email: contact@insidelab.com

---

**마지막 업데이트**: 2025-12-22
