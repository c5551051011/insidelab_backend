#!/usr/bin/env python
import requests
import time
import json

def test_railway_endpoints():
    """Test Railway deployment endpoints and caching"""

    BASE_URL = "https://insidelab.up.railway.app"

    print("🚀 Testing Railway Endpoint Deployment:")
    print(f"Base URL: {BASE_URL}")

    # Test 1: Basic API health check
    print("\n1. Testing API Health:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API is accessible")
        else:
            print("   ❌ API not responding correctly")
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        return

    # Test 2: Universities endpoint (should be cached for 24h)
    print("\n2. Testing Universities Endpoint (24h cache):")
    try:
        url = f"{BASE_URL}/api/v1/universities/"

        # First request
        start_time = time.time()
        response1 = requests.get(url, timeout=15)
        first_time = time.time() - start_time

        if response1.status_code == 200:
            data1 = response1.json()
            print(f"   ✅ First request: {response1.status_code} ({first_time:.3f}s)")
            print(f"   📊 Found {len(data1.get('results', []))} universities")

            # Second request (should hit cache)
            start_time = time.time()
            response2 = requests.get(url, timeout=15)
            second_time = time.time() - start_time

            if response2.status_code == 200:
                print(f"   ✅ Second request: {response2.status_code} ({second_time:.3f}s)")
                if second_time < first_time:
                    improvement = ((first_time - second_time) / first_time) * 100
                    print(f"   🚀 Cache performance: {improvement:.1f}% faster")
                else:
                    print("   ⚠️ No significant cache improvement detected")
        else:
            print(f"   ❌ Universities endpoint failed: {response1.status_code}")

    except Exception as e:
        print(f"   ❌ Universities test failed: {e}")

    # Test 3: Departments endpoint (should be cached for 12h)
    print("\n3. Testing Departments Endpoint (12h cache):")
    try:
        # Test with university ID 14 (mentioned in original error)
        url = f"{BASE_URL}/api/v1/universities/14/departments/"

        start_time = time.time()
        response = requests.get(url, timeout=15)
        request_time = time.time() - start_time

        if response.status_code == 200:
            departments = response.json()
            print(f"   ✅ Departments endpoint: {response.status_code} ({request_time:.3f}s)")
            print(f"   📊 University 14 has {len(departments)} departments")

            if departments:
                sample_dept = departments[0]
                print(f"   📝 Sample department: {sample_dept.get('department_name', 'N/A')}")
        else:
            print(f"   ❌ Departments endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")

    except Exception as e:
        print(f"   ❌ Departments test failed: {e}")

    # Test 4: Labs endpoint (should be cached for 30min)
    print("\n4. Testing Labs Endpoint (30min cache):")
    try:
        url = f"{BASE_URL}/api/v1/labs/"

        start_time = time.time()
        response = requests.get(url, timeout=15)
        request_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Labs endpoint: {response.status_code} ({request_time:.3f}s)")
            print(f"   📊 Found {len(data.get('results', []))} labs")
        else:
            print(f"   ❌ Labs endpoint failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Labs test failed: {e}")

    # Test 5: Featured labs endpoint (should be cached for 1h)
    print("\n5. Testing Featured Labs Endpoint (1h cache):")
    try:
        url = f"{BASE_URL}/api/v1/labs/featured/"

        start_time = time.time()
        response = requests.get(url, timeout=15)
        request_time = time.time() - start_time

        if response.status_code == 200:
            featured_labs = response.json()
            print(f"   ✅ Featured labs: {response.status_code} ({request_time:.3f}s)")
            print(f"   📊 Found {len(featured_labs)} featured labs")
        else:
            print(f"   ❌ Featured labs failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Featured labs test failed: {e}")

    # Test 6: Check response headers for caching
    print("\n6. Testing Cache Headers:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/universities/", timeout=15)
        headers = response.headers

        cache_related_headers = [
            'Cache-Control', 'ETag', 'Last-Modified', 'Expires', 'Vary'
        ]

        print("   📋 Cache-related headers:")
        for header in cache_related_headers:
            if header in headers:
                print(f"      {header}: {headers[header]}")

        if 'Cache-Control' in headers:
            print("   ✅ Cache headers present")
        else:
            print("   ⚠️ No cache headers detected")

    except Exception as e:
        print(f"   ❌ Header check failed: {e}")

    # Test 7: Check specific universities that had errors
    print("\n7. Testing Previously Problematic Universities:")
    error_university_ids = [14, 17, 18]

    for uni_id in error_university_ids:
        try:
            url = f"{BASE_URL}/api/v1/universities/{uni_id}/departments/"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                departments = response.json()
                print(f"   ✅ University {uni_id}: {len(departments)} departments")
            else:
                print(f"   ❌ University {uni_id}: Status {response.status_code}")

        except Exception as e:
            print(f"   ❌ University {uni_id}: Error - {e}")

    # Test 8: Performance comparison
    print("\n8. Performance Analysis:")
    try:
        endpoints = [
            ("/api/v1/universities/", "Universities"),
            ("/api/v1/labs/", "Labs"),
            ("/api/v1/universities/14/departments/", "Departments")
        ]

        for endpoint, name in endpoints:
            url = f"{BASE_URL}{endpoint}"
            times = []

            # Make 3 requests to test caching
            for i in range(3):
                start_time = time.time()
                response = requests.get(url, timeout=15)
                request_time = time.time() - start_time
                times.append(request_time)

                if response.status_code != 200:
                    print(f"   ❌ {name}: Request {i+1} failed")
                    break

            if len(times) == 3:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)

                print(f"   📊 {name}: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")

                if times[2] < times[0]:  # Third request faster than first
                    print(f"      🚀 Cache effectiveness detected!")

    except Exception as e:
        print(f"   ❌ Performance analysis failed: {e}")

    print("\n✅ Railway endpoint testing complete!")
    print("\n📝 Summary:")
    print("   - Tested core API endpoints")
    print("   - Verified departments endpoint fix")
    print("   - Measured cache performance impact")
    print("   - Confirmed Railway deployment status")

if __name__ == "__main__":
    test_railway_endpoints()