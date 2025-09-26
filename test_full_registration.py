#!/usr/bin/env python
import requests
import json

def test_registration_api():
    print("Testing full registration API with email verification...")

    # API endpoint
    url = "http://localhost:8000/api/v1/auth/register/"

    # Test data
    test_data = {
        "email": "fulltest@gmail.com",
        "username": "fulltest",
        "name": "Full Test User",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }

    try:
        # Make registration request
        response = requests.post(url, json=test_data)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            response_data = response.json()
            if response_data.get('email_sent'):
                print("✅ Full registration test PASSED!")
                print("✅ Email verification is working!")
            else:
                print("❌ Registration succeeded but email was not sent")
        else:
            print("❌ Registration failed")

    except Exception as e:
        print(f"❌ Test ERROR: {str(e)}")

if __name__ == "__main__":
    test_registration_api()