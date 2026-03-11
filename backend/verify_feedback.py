import sys
import os
import json

# Add the current directory to the path so we can import the app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app import create_app
    from models import db, User, Student, Tutor, Feedback
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def verify_feedback():
    print("Setting up test app...")
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # 1. Create Data
        print("Creating test data...")
        
        # Student
        student_user = User(name="Test Student", email="student@test.com", password="hash", role="student")
        db.session.add(student_user)
        db.session.commit()
        student = Student(user_id=student_user.id, interests="maths calculus")
        db.session.add(student)
        
        # Tutor (Anita - Maths)
        tutor_user = User(name="Anita", email="anita@test.com", password="hash", role="tutor")
        db.session.add(tutor_user)
        db.session.commit()
        tutor = Tutor(user_id=tutor_user.id, subjects="maths algebra calculus", rating=0.0)
        db.session.add(tutor)
        
        db.session.commit()
        
        client = app.test_client()
        
        # 2. Get Initial Recommendation Score
        print("\n[Step 1] Initial Recommendation Request...")
        resp = client.get(f'/api/recommend_tutors/{student.id}')
        initial_score = 0
        if resp.status_code == 200:
            data = resp.get_json()
            recs = data.get('recommendations', [])
            if recs:
                target = next((r for r in recs if r['tutor_id'] == tutor.id), None)
                if target:
                    initial_score = target['score']
                    print(f"Initial Score for Anita: {initial_score}")
                else:
                    print("Anita not found in recommendations.")
        else:
            print(f"Failed to get recommendations: {resp.status_code}")

        # 3. Submit 5-star Feedback
        print("\n[Step 2] Submitting 5-star Feedback...")
        feedback_data = {
            "student_id": student.id,
            "tutor_id": tutor.id,
            "rating": 5,
            "comment": "Great teacher!"
        }
        resp = client.post('/api/feedback', json=feedback_data)
        if resp.status_code == 201:
            print("Feedback submitted successfully.")
        else:
            print(f"Feedback submission failed: {resp.status_code} - {resp.get_json()}")
            
        # 4. Verify Tutor Rating Updated in DB
        updated_tutor = Tutor.query.get(tutor.id)
        print(f"Updated Tutor Rating in DB: {updated_tutor.rating}")
        if updated_tutor.rating == 5.0:
             print("[PASS] Tutor rating updated correctly.")
        else:
             print(f"[FAIL] Tutor rating incorrect (Expected 5.0).")

        # 5. Get Updated Recommendation Score
        print("\n[Step 3] Requesting Recommendations Again...")
        resp = client.get(f'/api/recommend_tutors/{student.id}')
        new_score = 0
        if resp.status_code == 200:
            data = resp.get_json()
            recs = data.get('recommendations', [])
            if recs:
                target = next((r for r in recs if r['tutor_id'] == tutor.id), None)
                if target:
                    new_score = target['score']
                    print(f"New Score for Anita: {new_score}")
                else:
                    print("Anita not found in recommendations.")
        
        # 6. Verify Boost
        # Boost formula: (Rating / 5.0) * 0.1
        # For rating 5.0, boost is 0.1
        expected_boost = 0.1
        actual_diff = new_score - initial_score
        
        print(f"\nScore Difference: {actual_diff:.4f}")
        
        # Allow small float point tolerance
        if abs(actual_diff - expected_boost) < 0.001:
             print("[PASS] Recommendation score boosted correctly.")
        else:
             print("[FAIL] Recommendation score boost mismatch.")

if __name__ == "__main__":
    verify_feedback()
