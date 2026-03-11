import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_user_removal():
    # 1. Register a test student
    test_user = {
        "name": "Test User To Remove",
        "email": "testremove@example.com",
        "password": "password123",
        "role": "student",
        "class_level": "Grade 10",
        "interests": "Testing"
    }
    
    print("Registering test user...")
    reg_res = requests.post(f"{BASE_URL}/register", json=test_user)
    if reg_res.status_code != 201:
        print(f"Registration failed: {reg_res.text}")
        return
    
    user_id = reg_res.json().get('id')
    print(f"Test user registered with ID: {user_id}")
    
    # 2. Verify login works
    print("Verifying login works...")
    login_res = requests.post(f"{BASE_URL}/login", json={"email": test_user['email'], "password": test_user['password']})
    if login_res.status_code == 200:
        print("Login successful.")
    else:
        print(f"Login failed: {login_res.text}")
        return

    # 3. Delete user via admin API
    print(f"Deleting user {user_id} via admin API...")
    del_res = requests.delete(f"{BASE_URL}/admin/users/{user_id}")
    if del_res.status_code == 200:
        print("User removed successfully.")
    else:
        print(f"Removal failed: {del_res.text}")
        return

    # 4. Verify login fails
    print("Verifying login fails now...")
    login_res_after = requests.post(f"{BASE_URL}/login", json={"email": test_user['email'], "password": test_user['password']})
    if login_res_after.status_code == 401:
        print("Login failed as expected. Verification successful.")
    else:
        print(f"Unexpected login result: {login_res_after.status_code}")

if __name__ == "__main__":
    test_user_removal()
