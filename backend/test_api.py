#!/usr/bin/env python3
"""
Simple test script for the FastAPI email verification endpoints
Run this after starting the FastAPI server
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ Health Check:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print("\n📝 User Registration:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Registration Failed: {e}")
        return False

def test_resend_verification():
    """Test resend verification code"""
    email_data = {"email": "test@example.com"}
    try:
        response = requests.post(f"{BASE_URL}/auth/resend-verification", json=email_data)
        print("\n🔄 Resend Verification:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Resend Failed: {e}")
        return False

def test_email_verification(verification_code):
    """Test email verification with code"""
    verify_data = {
        "email": "test@example.com",
        "code": verification_code
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/verify-email", json=verify_data)
        print(f"\n🔐 Email Verification (Code: {verification_code}):")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        return False

def test_get_user():
    """Test getting user information"""
    try:
        response = requests.get(f"{BASE_URL}/users/test@example.com")
        print("\n👤 Get User Info:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get User Failed: {e}")
        return False

def test_quick_analyze():
    """Test quick analyze endpoint"""
    analyze_data = {"url": "https://example.com"}
    try:
        response = requests.post(f"{BASE_URL}/analyze/quick", json=analyze_data)
        print("\n🔍 Quick Analyze:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Quick Analyze Failed: {e}")
        return False

def main():
    print("🚀 Testing SG AI Backend API")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Server not running. Start with: uvicorn main:app --reload")
        return
    
    # Test registration
    if not test_user_registration():
        return
    
    # Test resend (for already registered user)
    test_resend_verification()
    
    # Get verification code from user
    print("\n📨 Check the console output of your FastAPI server for the verification code.")
    verification_code = input("Enter the 6-digit verification code: ").strip()
    
    if len(verification_code) != 6 or not verification_code.isdigit():
        print("❌ Invalid verification code format")
        return
    
    # Test verification
    test_email_verification(verification_code)
    
    # Test get user
    test_get_user()
    
    # Test quick analyze
    test_quick_analyze()
    
    print("\n✅ API testing completed!")

if __name__ == "__main__":
    main() 