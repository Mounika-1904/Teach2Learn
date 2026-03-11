from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import os

def reset_passwords():
    app = create_app()
    with app.app_context():
        # Update Student
        student = User.query.filter_by(email='mounika@gmail.com').first()
        if student:
            student.password = generate_password_hash('password123')
            print("Password for mounika@gmail.com set to: password123")
        
        # Update Admin
        admin = User.query.filter_by(email='admin@teach2learn.com').first()
        if admin:
            admin.password = generate_password_hash('admin123')
            print("Password for admin@teach2learn.com set to: admin123")
        else:
            # Create admin if it doesn't exist
            admin = User(
                name="System Admin",
                email="admin@teach2learn.com",
                password=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin)
            print("Admin account created with password: admin123")
            
        db.session.commit()

if __name__ == "__main__":
    reset_passwords()
