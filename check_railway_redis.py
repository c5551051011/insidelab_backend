#!/usr/bin/env python
"""
Railway Redis 상태 확인 스크립트
"""
import requests
import json

def check_railway_redis():
    """Railway 환경에서 Redis 동작 확인"""

    BASE_URL = "https://insidelab.up.railway.app"

    print("🔍 Railway Redis 상태 확인:")
    print(f"   Base URL: {BASE_URL}")

    # 1. 캐시 상태 확인 엔드포인트 생성이 필요
    print("\n📋 Redis 확인 방법:")
    print("   1. Railway 대시보드에서 Redis 서비스 추가")
    print("   2. REDIS_URL 환경변수 설정")
    print("   3. 아래 엔드포인트들로 확인")

    # 2. 캐시 테스트를 위한 API 호출
    endpoints_to_test = [
        ("/api/v1/universities/", "Universities"),
        ("/api/v1/labs/", "Labs"),
        ("/api/v1/universities/14/departments/", "Departments")
    ]

    print("\n🧪 캐시 성능 테스트:")

    for endpoint, name in endpoints_to_test:
        url = f"{BASE_URL}{endpoint}"

        try:
            # 첫 번째 요청 (캐시 생성)
            import time
            start = time.time()
            response1 = requests.get(url, timeout=10)
            time1 = time.time() - start

            # 두 번째 요청 (캐시에서 읽기)
            start = time.time()
            response2 = requests.get(url, timeout=10)
            time2 = time.time() - start

            if response1.status_code == 200 and response2.status_code == 200:
                improvement = ((time1 - time2) / time1) * 100 if time1 > time2 else 0
                print(f"   ✅ {name}:")
                print(f"      첫 번째 요청: {time1:.3f}s")
                print(f"      두 번째 요청: {time2:.3f}s")

                if improvement > 5:
                    print(f"      🚀 캐시 효과: {improvement:.1f}% 개선 (Redis 동작 중)")
                elif improvement > 0:
                    print(f"      📈 약간의 개선: {improvement:.1f}% (캐시 효과 있음)")
                else:
                    print(f"      📊 성능 변화 없음 (DummyCache 또는 캐시 미스)")
            else:
                print(f"   ❌ {name}: HTTP {response1.status_code}")

        except Exception as e:
            print(f"   ❌ {name}: 오류 - {e}")

    # 3. 캐시 헤더 확인
    print("\n🔧 캐시 헤더 확인:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/universities/", timeout=10)
        headers = response.headers

        cache_headers = ['Cache-Control', 'ETag', 'Last-Modified', 'Expires', 'Vary']
        for header in cache_headers:
            if header in headers:
                print(f"   📋 {header}: {headers[header]}")

        if 'Cache-Control' in headers:
            print("   ✅ 캐시 헤더 존재 (캐시 시스템 동작 중)")
        else:
            print("   ⚠️ 캐시 헤더 없음")

    except Exception as e:
        print(f"   ❌ 헤더 확인 실패: {e}")

    print("\n📝 Redis 상태 판단:")
    print("   🟢 Redis 동작 중: 5% 이상 성능 개선 + 캐시 헤더")
    print("   🟡 부분적 캐시: 약간의 성능 개선")
    print("   🔴 DummyCache: 성능 개선 없음")

    print("\n💡 Railway에서 Redis 활성화하는 방법:")
    print("   1. Railway 프로젝트 대시보드 접속")
    print("   2. '+ New Service' → 'Add Service' → 'Redis' 선택")
    print("   3. 환경변수에 REDIS_URL 자동 생성됨")
    print("   4. 앱 재배포 후 Redis 활성화")

if __name__ == "__main__":
    check_railway_redis()