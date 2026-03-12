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
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        
        # Supabase requires SSL. Ensure sslmode=require is in the URL if not present.
        if "postgresql" in _db_url and "sslmode=" not in _db_url:
            separator = "&" if "?" in _db_url else "?"
            _db_url += f"{separator}sslmode=require"
    
    SQLALCHEMY_DATABASE_URI = _db_url or f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db'))}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
