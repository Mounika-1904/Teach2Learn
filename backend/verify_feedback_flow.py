import requests

BASE_URL = "http://127.0.0.1:5000/api"

def verify_feedback_flow():
    # 1. Register a student
    student_email = "feedbacktest@example.com"
    reg_data = {
        "name": "Feedback Tester",
        "email": student_email,
        "password": "password123",
        "role": "student",
        "class_level": "Grade 11",
        "interests": "Math"
    }
    requests.post(f"{BASE_URL}/register", json=reg_data)
    
    # 2. Login
    login_res = requests.post(f"{BASE_URL}/login", json={"email": student_email, "password": "password123"})
    login_data = login_res.json()
    student_id = login_data['role_id']
    
    # 3. Get a tutor
    tutors_res = requests.get(f"{BASE_URL}/search_tutors?query=")
    tutors = tutors_res.json()
    if not tutors:
        print("No tutors found")
        return
    tutor_id = tutors[0]['id']
    
    # 4. Book a session
    booking_data = {
        "student_id": student_id,
        "tutor_id": tutor_id,
        "subject": "Math",
        "date": "2026-03-20",
        "time": "10:00 AM"
    }
    book_res = requests.post(f"{BASE_URL}/schedule/book", json=booking_data)
    session_id = book_res.json()['id']
    print(f"Booked session: {session_id}")
    
    # 5. Mark as completed
    comp_res = requests.put(f"{BASE_URL}/schedule/complete/{session_id}")
    print(f"Completion status: {comp_res.status_code}")
    
    # 6. Submit feedback
    feedback_data = {
        "student_id": student_id,
        "tutor_id": tutor_id,
        "rating": 5,
        "comment": "Excellent session! The new UI is great.",
        "student_skill_level": "Good"
    }
    feed_res = requests.post(f"{BASE_URL}/feedback", json=feedback_data)
    print(f"Feedback status: {feed_res.status_code}")
    
    # 7. Verify in admin feedback API
    admin_feed_res = requests.get(f"{BASE_URL}/admin/feedback")
    all_feedback = admin_feed_res.json()
    found = any(f['comment'] == feedback_data['comment'] for f in all_feedback)
    if found:
        print("Feedback verification SUCCESSFUL.")
    else:
        print("Feedback verification FAILED.")

if __name__ == "__main__":
    verify_feedback_flow()
