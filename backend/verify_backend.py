import sys
import os

# Add the current directory to the path so we can import the app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app import create_app
    from models import db
    print("Successfully imported app and db.")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def verify_app():
    print("Creating app instance...")
    app = create_app()
    app.config['TESTING'] = True
    
    print("Creating test client...")
    client = app.test_client()
    
    print("Checking status route...")
    response = client.get('/api/status')
    
    if response.status_code == 200:
        print(f"Status check passed: {response.json}")
    else:
        print(f"Status check failed: {response.status_code}")
        sys.exit(1)

    print("Checking database creation...")
    db_path = os.path.join(app.root_path, 'database.db')
    if os.path.exists(db_path):
         print(f"Database found at {db_path}")
    else:
         print(f"Warning: Database file not found at {db_path} (it might be in memory or lazy created)")

if __name__ == "__main__":
    verify_app()
