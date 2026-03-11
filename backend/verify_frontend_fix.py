import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from models import db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret'

def verify_fix():
    print("--- Verifying Frontend Fallback Fix ---")
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        # NOTE: WE ARE NOT CREATING STUDENT 2 IN THE DB
        # This simulates the user's empty DB state
        
        client = app.test_client()
        
        print("\nRequesting recommendations for Student 2 (Not in DB)...")
        resp = client.get('/api/recommend_tutors/2')
        
        if resp.status_code == 200:
            print("[PASS] API returned 200 OK.")
            data = resp.get_json()
            recs = data.get('recommendations', [])
            print(f"Recommendations count: {len(recs)}")
            if len(recs) > 0:
                print(f"Top Recommendation: {recs[0]['name']}")
                print("[PASS] Recommendations returned successfully using dummy fallback.")
            else:
                print("[FAIL] No recommendations returned.")
        else:
             print(f"[FAIL] API returned {resp.status_code} - {resp.get_json()}")

if __name__ == "__main__":
    verify_fix()
