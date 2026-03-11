import sys
import os
import json
import time

# Add the current directory to the path so we can import the app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app import create_app
    from models import db, User, Student, Tutor
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def verify_auth():
    print("Setting up test app...")
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        # Verify schema
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('user')]
        print(f"User table columns: {columns}")
        
    client = app.test_client()
    
    # 1. Test Registration
    print("\n[1] Testing Registration...")
    student_data = {
        "name": "Test Student",
        "email": "student@test.com",
        "password": "password123",
        "role": "student"
    }
    
    response = client.post('/api/register', 
                          data=json.dumps(student_data),
                          content_type='application/json')
    
    if response.status_code == 201:
        print("[PASS] Registration successful")
    else:
        print(f"[FAIL] Registration failed: {response.status_code} - {response.get_json()}")
        sys.exit(1)

    # 2. Test Duplicate Registration
    print("\n[2] Testing Duplicate Registration...")
    response = client.post('/api/register', 
                          data=json.dumps(student_data),
                          content_type='application/json')
    
    if response.status_code == 409:
        print("[PASS] Duplicate check passed")
    else:
        print(f"[FAIL] Duplicate check failed: {response.status_code}")

    # 3. Test Login Success
    print("\n[3] Testing Login Success...")
    login_data = {
        "email": "student@test.com",
        "password": "password123"
    }
    
    response = client.post('/api/login', 
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    if response.status_code == 200:
        data = response.get_json()
        if data['user']['email'] == "student@test.com" and data['user']['role'] == "student":
            print("[PASS] Login successful and data correct")
        else:
             print(f"[FAIL] Login data incorrect: {data}")
    else:
        print(f"[FAIL] Login failed: {response.status_code}")

    # 4. Test Login Failure
    print("\n[4] Testing Login Failure...")
    bad_login_data = {
        "email": "student@test.com",
        "password": "wrongpassword"
    }
    
    response = client.post('/api/login', 
                          data=json.dumps(bad_login_data),
                          content_type='application/json')
    
    if response.status_code == 401:
        print("[PASS] Login failure check passed")
    else:
        print(f"[FAIL] Login failure check failed (expected 401, got {response.status_code})")

if __name__ == "__main__":
    verify_auth()
