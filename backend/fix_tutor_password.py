from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def fix_password():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='bhavya@gmail.com').first()
        if user:
            user.password = generate_password_hash('bhavya@1601')
            db.session.commit()
            print("Successfully updated password for bhavya@gmail.com to bhavya@1601")
        else:
            print("User bhavya@gmail.com not found")

if __name__ == "__main__":
    fix_password()
