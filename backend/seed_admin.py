from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def seed_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin_email = "admin@teach2learn.com"
        existing = User.query.filter_by(email=admin_email).first()
        if existing:
            print(f"Admin user {admin_email} already exists.")
            return

        hashed_password = generate_password_hash("admin123")
        admin = User(
            name="System Admin",
            email=admin_email,
            password=hashed_password,
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user {admin_email} seeded successfully.")

if __name__ == "__main__":
    seed_admin()
