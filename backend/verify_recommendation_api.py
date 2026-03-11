import sys
import os
import json

# Add the current directory to the path so we can import the app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app import create_app
    from models import db, User, Student, Tutor
    from ml.recommendation import RecommendationEngine
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def verify_api():
    print("Setting up test app...")
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # 1. Create Data
        print("Creating test data...")
        
        # Student wanting Physics
        student_user = User(name="Physics Fan", email="student@test.com", password="hash", role="student")
        db.session.add(student_user)
        db.session.commit() # Commit to get ID
        
        student = Student(user_id=student_user.id, interests="I struggle with Physics and Mechanics")
        db.session.add(student)
        
        # Tutors
        tutor_users = [
            ("Math Tutor", "math@test.com", "Algebra Geometry"),
            ("Physics Tutor", "physics@test.com", "Physics Mechanics Thermodynamics"),
            ("English Tutor", "english@test.com", "Literature Grammar"),
            ("Science Tutor", "science@test.com", "Physics Chemistry Biology")
        ]
        
        for name, email, subjects in tutor_users:
            u = User(name=name, email=email, password="hash", role="tutor")
            db.session.add(u)
            db.session.commit()
            t = Tutor(user_id=u.id, subjects=subjects)
            db.session.add(t)
            
        db.session.commit()
        
        # 2. Call API
        # Note: The API currently uses DUMMY data from the ML module, ignoring the DB text.
        # Student 1 in DUMMY_STUDENTS has interests: "maths calculus"
        # We expect recommendations for Math (Anita).
        
        client = app.test_client()
        print(f"Requesting recommendations for student 1 (Dummy Interest: 'maths calculus')...")
        
        response = client.get(f'/api/recommend_tutors/1')
        
        if response.status_code == 200:
            data = response.get_json()
            recommendations = data.get('recommendations', [])
            print(f"\nAPI returned {len(recommendations)} recommendations for Student 1:")
            
            for idx, rec in enumerate(recommendations, 1):
                print(f"{idx}. {rec['name']} (Score: {rec['score']})")
                
            # Verification Logic
            if len(recommendations) > 0 and recommendations[0]['name'] == "Anita":
                 print("\n[PASS] Top recommendation matches dummy interest (Anita).")
            else:
                 print("\n[FAIL] Unexpected top recommendation.")

        # 3. Call API for Student 2
        print(f"\nRequesting recommendations for student 2 (Dummy Interest: 'python ai')...")
        response = client.get(f'/api/recommend_tutors/2')
        
        if response.status_code == 200:
            data = response.get_json()
            recommendations = data.get('recommendations', [])
            print(f"\nAPI returned {len(recommendations)} recommendations for Student 2:")
            
            for idx, rec in enumerate(recommendations, 1):
                print(f"{idx}. {rec['name']} (Score: {rec['score']})")
                
            # Verification Logic for Student 2 (Expect Ravi)
            if len(recommendations) > 0 and recommendations[0]['name'] == "Ravi":
                 print("\n[PASS] Top recommendation matches dummy interest (Ravi).")
            else:
                 print("\n[FAIL] Unexpected top recommendation for Student 2.")
                 
        else:
            print(f"\n[FAIL] API request failed: {response.status_code} - {response.get_json()}")

if __name__ == "__main__":
    verify_api()
