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

    # 1. Register blueprints first
    app.register_blueprint(main)

    # 2. Specific API/Health routes
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "teach2learn-backend"}), 200

    @app.route('/debug/routes')
    def list_routes():
        import urllib
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
            output.append(line)
        return "<pre>" + "\n".join(sorted(output)) + "</pre>"

    # 3. Static files and Home
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        # Allow specific file paths to be served
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return app.send_static_file(path)
        
        # If it looks like an API call but wasn't caught by the blueprint, it's a 404
        if path.startswith('api/'):
            return jsonify({"error": f"API route '{path}' not found"}), 404
            
        # Fallback to index for SPA routing
        return app.send_static_file('index.html')

    # 4. Global Error Logger (Crucial for Railway debugging)
    @app.errorhandler(Exception)
    def handle_exception(e):
        print("!!! GLOBAL EXCEPTION CAUGHT !!!")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

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
            print("DB_INIT: Checking for existing tables...")
            # Simple check for existing table (e.g. User) to avoid heavy db.create_all() every time
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'user' in inspector.get_table_names():
                print("DB_INIT: Tables already exist. Skipping create_all.")
            else:
                print("DB_INIT: Tables missing. Running create_all...")
                db.create_all()
                print("DB_INIT: Database tables created.")
            
        except Exception as e:
            print(f"CRITICAL ERROR during database init: {str(e)}")
            import traceback
            traceback.print_exc()
            # On Railway, sometimes the first connection fails. We can try to continue
            # if the variables are set, the app might recover inside a request.

    return app

