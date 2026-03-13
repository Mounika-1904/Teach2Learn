import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
db_url = os.environ.get('DATABASE_URL')
if db_url:
    print(f"DEBUG: Using DATABASE_URL from environment (starts with: {db_url[:10]}...)")
else:
    print("DEBUG: DATABASE_URL not found in environment. Falling back to SQLite.")

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database Configuration
    # Railway provides DATABASE_URL. We need to ensure it's postgresql:// not postgres://
    _db_url = os.environ.get('DATABASE_URL')
    
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        
        # In cloud environments like Railway, sometimes SSL is required for Postgres
        if "postgresql" in _db_url and "sslmode" not in _db_url:
            if "?" in _db_url:
                _db_url += "&sslmode=prefer"
            else:
                _db_url += "?sslmode=prefer"
                
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Fallback to local SQLite ONLY for local development
        # In production (Railway), this will likely fail due to read-only FS, which is actually helpful 
        # because it prevents silent failures and helps us see the error in logs.
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db'))}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
