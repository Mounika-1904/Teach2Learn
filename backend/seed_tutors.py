import sys
import os

# Add the current directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Tutor, Student
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    with app.app_context():
        # 1. Seed Tutors
        tutors_to_add = [
            ("Dr. Aris", "aris@example.com", "Artificial Intelligence, Machine Learning, Deep Learning, NLP", "15 years", 4.9),
            ("Prof. Khanna", "khanna@example.com", "Computer Networks, Distributed Systems, Cloud Computing", "12 years", 4.7),
            ("Sarah Miller", "sarah@example.com", "Data Structures, Algorithms, Software Engineering, Compiler Design", "8 years", 4.5),
            ("James Watt", "james@example.com", "Thermodynamics, Heat Transfer, Fluid Mechanics, Robotics", "20 years", 4.8),
            ("Elena Volt", "elena@example.com", "Power Systems, Electrical Machines, Control Systems, Power Electronics", "10 years", 4.6),
            ("Vikas Gupta", "vikas@example.com", "VLSI, Embedded Systems, Microprocessors, Digital Signal Processing", "7 years", 4.4),
            ("Rohan Das", "rohan@example.com", "Structural Engineering, Geotechnical Engineering, Environmental Engineering", "5 years", 4.2),
            ("Anita Desai", "anita@example.com", "Linear Algebra, Probability & Statistics, Optimization, Numerical Methods", "6 years", 4.7),
            ("Sanjay Mehra", "sanjay@example.com", "Operating Systems, DBMS, Big Data, Cloud Computing", "9 years", 4.6),
            ("Lisa Wang", "lisa@example.com", "Computer Vision, Image Processing, IoT, Blockchain", "4 years", 4.3),
            ("Mark Steel", "mark@example.com", "Manufacturing Technology, Mechanical Design, Thermodynamics", "11 years", 4.5),
            ("Alice Green", "alice@example.com", "Transportation Engineering, Civil Design, Urban Planning", "3 years", 4.0),
            ("Cyber Ninja", "security@example.com", "Cyber Security, Ethical Hacking, Network Security", "10 years", 4.9)
        ]
        
        for name, email, subjects, exp, rating in tutors_to_add:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(name=name, email=email, password=generate_password_hash("password123"), role='tutor')
                db.session.add(user)
                db.session.flush()
                tutor = Tutor(user_id=user.id, subjects=subjects, experience=exp, rating=rating)
                db.session.add(tutor)
            else:
                tutor = user.tutor_profile
                if tutor:
                    tutor.subjects = subjects
                    tutor.experience = exp
                    tutor.rating = rating

        # 2. Seed Test Student
        student_email = "mounika@gmail.com"
        user = User.query.filter_by(email=student_email).first()
        if not user:
            print(f"Creating test student: {student_email}")
            user = User(name="Mounika", email=student_email, password=generate_password_hash("password123"), role='student')
            db.session.add(user)
            db.session.flush()
            student = Student(user_id=user.id, class_level="B.Tech", interests="Machine Learning")
            db.session.add(student)
        
        db.session.commit()
        print("Database seeded successfully with tutors and a test student.")

if __name__ == "__main__":
    seed_database()
