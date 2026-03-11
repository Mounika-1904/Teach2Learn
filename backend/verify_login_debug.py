from app import create_app
from models import db, User
from werkzeug.security import check_password_hash
import requests

def debug_login(email, password):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"DEBUG: User {email} not found in database.")
            return
        
        print(f"DEBUG: User {email} found.")
        print(f"DEBUG: Role: {user.role}")
        print(f"DEBUG: Hashed Password starts with: {user.password[:20]}...")
        
        is_match = check_password_hash(user.password, password)
        print(f"DEBUG: check_password_hash result for '{password}': {is_match}")
        
        # Test the actual API endpoint
        url = "http://127.0.0.1:5000/api/login"
        try:
            resp = requests.post(url, json={"email": email, "password": password})
            print(f"DEBUG: API Status: {resp.status_code}")
            print(f"DEBUG: API Response: {resp.json()}")
        except Exception as e:
            print(f"DEBUG: API Call Error: {e}")

if __name__ == "__main__":
    # Test for the user's tutor account with provided password
    debug_login("bhavya@gmail.com", "bhavya@1601")
    print("-" * 30)
    # Test for seeded tutor
    debug_login("aris@example.com", "password123")
