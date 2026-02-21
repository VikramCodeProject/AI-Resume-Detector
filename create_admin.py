"""
Quick Admin User Registration
Run this to create your admin account
"""
import requests
import json

# Backend URL
API_URL = "http://localhost:8000/api"

# Admin credentials - CHANGE THESE!
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
ADMIN_NAME = "System Administrator"

print("=" * 50)
print("Creating Admin User Account")
print("=" * 50)
print()

# Register admin user
register_data = {
    "email": ADMIN_EMAIL,
    "password": ADMIN_PASSWORD,
    "full_name": ADMIN_NAME,
    "gdpr_consent": True
}

try:
    print(f"📝 Registering user: {ADMIN_EMAIL}")
    response = requests.post(f"{API_URL}/auth/register", json=register_data)
    
    if response.status_code == 200:
        print("✅ Registration successful!")
        result = response.json()
        print(f"   User ID: {result.get('user_id')}")
        print(f"   Email: {result.get('email')}")
        print()
        
        # Try to login
        print(f"🔐 Logging in with credentials...")
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            print("✅ Login successful!")
            print()
            print("=" * 50)
            print("YOUR ADMIN CREDENTIALS")
            print("=" * 50)
            print(f"Email:    {ADMIN_EMAIL}")
            print(f"Password: {ADMIN_PASSWORD}")
            print()
            print(f"Access Token: {tokens['access_token'][:50]}...")
            print()
            print("Use these credentials to login to the frontend!")
            print("Frontend URL: http://localhost:3000")
            print("=" * 50)
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    elif response.status_code == 400 and "already exists" in response.text:
        print("⚠️  User already exists!")
        print()
        print("=" * 50)
        print("YOUR LOGIN CREDENTIALS")
        print("=" * 50)
        print(f"Email:    {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print()
        print("Use these to login at: http://localhost:3000")
        print("=" * 50)
    else:
        print(f"❌ Registration failed: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend!")
    print("   Make sure the backend is running:")
    print("   cd backend")
    print("   python -m uvicorn main:app --reload")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("Next steps:")
print("1. Start frontend: cd frontend && npm run dev")
print("2. Open: http://localhost:3000")
print("3. Login with the credentials above")
print("4. Start uploading resumes!")
