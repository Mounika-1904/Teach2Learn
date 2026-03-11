from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'tutor'

    # Relationships using back_populates for explicit linking
    student_profile = db.relationship('Student', back_populates='user', uselist=False, cascade="all, delete-orphan")
    tutor_profile = db.relationship('Tutor', back_populates='user', uselist=False, cascade="all, delete-orphan")
    
    # Message relationships
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver', lazy='dynamic')

    # Notification relationship
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.name}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    class_level = db.Column(db.String(50))
    interests = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255))

    # Explicit back_populates
    user = db.relationship('User', back_populates='student_profile')
    given_feedback = db.relationship('Feedback', back_populates='student', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='student', lazy='dynamic')
    subject_levels = db.relationship('StudentSubjectLevel', back_populates='student', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Student {self.user.name if self.user else "Unknown"}>'

class StudentSubjectLevel(db.Model):
    __tablename__ = 'student_subject_level'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    subject = db.Column(db.String(100), nullable=False, index=True)
    skill_level = db.Column(db.String(50), nullable=False, index=True) # Weak, Average, Good, Excellent

    student = db.relationship('Student', back_populates='subject_levels')

    def __repr__(self):
        return f'<StudentSubjectLevel {self.subject}: {self.skill_level}>'

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    subjects = db.Column(db.String(200))
    experience = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    availability_info = db.Column(db.Text) # e.g., "Monday 9-11AM, Tuesday 2-4PM"

    # Explicit back_populates
    user = db.relationship('User', back_populates='tutor_profile')
    received_feedback = db.relationship('Feedback', back_populates='tutor', lazy='dynamic')
    schedules = db.relationship('Schedule', back_populates='tutor', lazy='dynamic')

    def __repr__(self):
        return f'<Tutor {self.user.name if self.user else "Unknown"}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    student_skill_level = db.Column(db.String(50), nullable=True, index=True)

    student = db.relationship('Student', back_populates='given_feedback')
    tutor = db.relationship('Tutor', back_populates='received_feedback')

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='upcoming')
    meeting_link = db.Column(db.String(200))

    student = db.relationship('Student', back_populates='schedules')
    tutor = db.relationship('Tutor', back_populates='schedules')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_messages')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'
