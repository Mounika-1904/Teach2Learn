import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable (default to 5000)
    port = int(os.environ.get("PORT", 5000))
    # Run the app binding to 0.0.0.0
    app.run(host='0.0.0.0', port=port)
