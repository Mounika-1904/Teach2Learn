import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:5000/api"

def test_full_application_flow():
    print("--- Starting End-to-End Persistence Test ---")
    
    # 0. Register a tutor
    tutor_email = f"tutor_{uuid.uuid4().hex[:6]}@example.com"
    tutor_reg_data = {
        "name": "Math Pro",
        "email": tutor_email,
        "password": "password123",
        "role": "tutor",
        "subjects": "Math, Calculus",
        "experience": "5 years"
    }
    print(f"\n[0] Registering tutor: {tutor_email}")
    res = requests.post(f"{BASE_URL}/register", json=tutor_reg_data)
    print(f"Status: {res.status_code}")
    assert res.status_code == 201
    
    # 1. Register a student
    student_email = f"tester_{uuid.uuid4().hex[:6]}@example.com"
    reg_data = {
        "name": "Test Student",
        "email": student_email,
        "password": "password123",
        "role": "student",
        "class_level": "Undergraduate",
        "interests": "Math, Coding"
    }
    
    print(f"\n[1] Registering student: {student_email}")
    res = requests.post(f"{BASE_URL}/register", json=reg_data)
    print(f"Status: {res.status_code}")
    assert res.status_code == 201
    
    # 2. Login
    print("\n[2] Logging in...")
    login_data = {"email": student_email, "password": "password123"}
    res = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    user_info = res.json()
    student_id = user_info['role_id']
    print(f"Logged in as {user_info['name']} (SID: {student_id})")
    
    # 3. Get Recommendations
    print(f"\n[3] Fetching recommendations for SID: {student_id}")
    res = requests.get(f"{BASE_URL}/recommend_tutors/{student_id}")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    recs = res.json().get('recommendations', [])
    print(f"Found {len(recs)} recommendations.")
    
    tutor_id = None
    if recs:
        # Find the tutor we just registered if possible
        for r in recs:
            if r['name'] == "Math Pro":
                tutor_id = r['tutor_id']
                break
        if not tutor_id:
            tutor_id = recs[0]['tutor_id']
            tutor_name = recs[0]['name']
            print(f"Selected tutor: {tutor_name} (ID: {tutor_id})")
    
    if not tutor_id:
        print("[FAIL] No tutors available for booking.")
        return

    # 4. Search Tutors
    print("\n[4] Testing Search for 'Math'...")
    res = requests.get(f"{BASE_URL}/tutors/search?q=Math")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    search_results = res.json()
    print(f"Found {len(search_results)} tutors matching 'Math'.")

    # 5. Book a Session
    print(f"\n[5] Booking session with tutor {tutor_id}...")
    book_data = {
        "student_id": student_id,
        "tutor_id": tutor_id,
        "subject": "Math Basics",
        "date": "28 Feb",
        "time": "10:30 AM"
    }
    res = requests.post(f"{BASE_URL}/schedule/book", json=book_data)
    print(f"Status: {res.status_code}")
    assert res.status_code == 201
    print("Session booked successfully.")

    # 6. Verify Schedule
    print(f"\n[6] Verifying schedule for SID: {student_id}")
    res = requests.get(f"{BASE_URL}/schedule/student/{student_id}")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    schedule = res.json()
    print(f"Appointments found: {len(schedule)}")
    assert len(schedule) > 0
    print(f"Upcoming: {schedule[0]['subject']} with {schedule[0]['tutor_name']} at {schedule[0]['time']}")

    print("\n--- [PASS] End-to-End Logic Test Successful ---")

if __name__ == "__main__":
    try:
        test_full_application_flow()
    except Exception as e:
        print(f"\n[FAIL] Test aborted with error: {e}")
        import traceback
        traceback.print_exc()
