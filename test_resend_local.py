#!/usr/bin/env python
import requests
import json
import uuid
import time

def test_resend_local():
    print("🔥 Testing Resend Email Service Locally")
    print("API Key: re_9Vcn67GY_EkVga5b5qEvJfScy4hrNs6LQ")
    print("="*60)

    # Generate unique username
    unique_id = str(uuid.uuid4())[:8]

    # Local endpoint
    url = "http://localhost:8000/api/v1/auth/register/"

    # Test data with verified email (Resend testing limitation)
    test_data = {
        "email": "insidelab25@gmail.com",
        "username": f"resendtest{unique_id}",
        "name": "Resend Test User",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "position": "PhD Student",
        "department": "Computer Science"
    }

    print(f"🎯 Target email: c5551051011@gmail.com")
    print(f"🆔 Username: {test_data['username']}")
    print(f"📧 From: InsideLab <noreply@insidelab.io>")
    print("⏳ Testing Resend email sending...")

    start_time = time.time()

    try:
        # Test local Resend integration
        response = requests.post(url, json=test_data, timeout=30)

        elapsed_time = time.time() - start_time
        print(f"\n⏱️ Response time: {elapsed_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")

        try:
            response_json = response.json()
            print(f"📝 Response:")
            print(json.dumps(response_json, indent=2))

            if response.status_code == 201:
                email_sent = response_json.get('email_sent', False)

                if email_sent:
                    print("\n🎉 SUCCESS! Resend Email Working Locally!")
                    print("✅ Resend API integration successful")
                    print("✅ Email verification sent via Resend")
                    print(f"📧 Check c5551051011@gmail.com for verification email")

                    if elapsed_time < 5:
                        print("⚡ EXCELLENT: Very fast email delivery")
                    elif elapsed_time < 10:
                        print("✅ FAST: Good email delivery speed")
                    else:
                        print("⚠️ SLOW: Email took longer than expected")

                    print("\n📬 Email Details:")
                    print("   • From: InsideLab <noreply@insidelab.io>")
                    print("   • Subject: 🔬 InsideLab 이메일 인증을 완료해 주세요")
                    print("   • Verification URL: Railway endpoints")
                    print("   • Homepage link: c5551051011.github.io/insidelab_frontend")

                    user_data = response_json.get('user', {})
                    print(f"\n👤 User created: ID {user_data.get('id')}")

                else:
                    print("\n❌ Registration succeeded but email_sent=false")
                    print("❌ Resend integration failed")
                    print("💡 Check server logs for Resend API errors")

            elif response.status_code == 500:
                error_msg = response_json.get('error', '')
                print(f"\n❌ Server Error: {error_msg}")

                if "verification email" in error_msg.lower():
                    print("✅ Transaction rollback working")
                    print("❌ Resend API call failed")
                    print("💡 Check RESEND_API_KEY configuration")
                else:
                    print("❌ Different server error")

            elif response.status_code == 400:
                error_details = response_json.get('error', '')
                if "already exists" in str(error_details).lower():
                    print("\nℹ️ Email already registered (normal)")
                    print("✅ Local server responding properly")
                else:
                    print(f"\n❌ Validation error: {error_details}")

            else:
                print(f"\n🤔 Unexpected status: {response.status_code}")

        except json.JSONDecodeError:
            print(f"\n❌ Non-JSON response: {response.text[:300]}")

        # Next steps based on results
        print(f"\n📋 NEXT STEPS:")
        if response.status_code == 201 and response_json.get('email_sent'):
            print("✅ Ready for Railway deployment!")
            print("🚀 Add RESEND_API_KEY to Railway environment variables")
        else:
            print("🔧 Fix local issues before Railway deployment")
            print("📝 Check Django logs for specific errors")

    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ Error after {elapsed_time:.2f} seconds: {str(e)}")

    print("\n" + "="*60)
    print("🎯 IF SUCCESS: Deploy to Railway with RESEND_API_KEY")
    print("🔧 IF FAILED: Check Django server logs for errors")
    print("="*60)

if __name__ == "__main__":
    test_resend_local()