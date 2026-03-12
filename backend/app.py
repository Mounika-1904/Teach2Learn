from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from flask_migrate import Migrate
from models import db
from routes import main

import os

def create_app(config_class=Config):
    # Set static folder to sibling frontend directory
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(main)

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "teach2learn-backend"}), 200

    # Route to serve frontend files
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return app.send_static_file(path)
        return app.send_static_file('index.html')

    # Database initialization
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        # Mask password for logs
        safe_uri = db_uri
        if '@' in db_uri:
            parts = db_uri.split('@')
            safe_uri = parts[0].split(':')[:2] # protocol and user
            safe_uri = ":".join(safe_uri) + ":****@" + parts[1]
        
        print(f"DATABASE ATTEMPT: {safe_uri}")
        
        try:
            if db_uri.startswith('sqlite'):
                db.create_all()
                print("SQLite database initialized.")
            else:
                print("PostgreSQL mode detected. Skipping db.create_all() to avoid startup delay.")
        except Exception as e:
            print(f"CRITICAL ERROR during database init: {e}")
            # Don't let the crash happen silently
            raise e

    return app

