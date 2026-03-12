import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app

print("MAIN: Starting application factory...")
app = create_app()
print("MAIN: Application factory initialized.")

# Optional: Run DB init separately if we are in the main worker
if os.environ.get('SKIP_DB_INIT') != 'true':
    with app.app_context():
        # The logic is already in app.py, but we can call it here if needed
        # or just rely on app.py which we will refine.
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"MAIN: Running dev server on port {port}...")
    app.run(host='0.0.0.0', port=port)
