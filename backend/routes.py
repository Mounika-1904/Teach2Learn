from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Student, Tutor, Feedback, Schedule, Message, Notification
from ml.recommendation import RecommendationEngine, SUBJECT_CORPUS
import difflib
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

# Upload configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'frontend', 'uploads', 'messaging')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ... (existing routes unchanged) ...

@main.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student').lower() # 'student' or 'tutor'

    if not all([name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.flush()

    if role == 'tutor':
        tutor = Tutor(user_id=user.id, subjects=data.get('subjects', ''), experience=data.get('experience', ''), availability_info=data.get('availability_info', ''))
        db.session.add(tutor)
    else:
        student = Student(user_id=user.id, class_level=data.get('class_level', ''), interests=data.get('interests', ''))
        db.session.add(student)

    db.session.commit()
    return jsonify({"message": "User registered successfully", "id": user.id}), 201

@main.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        # Safely retrieve role_id based on role and existence of profile
        role_id = None
        if user.role == 'student':
            if user.student_profile:
                role_id = user.student_profile.id
            else:
                return jsonify({"error": "Student profile not found for this user"}), 404
        elif user.role == 'tutor':
            if user.tutor_profile:
                role_id = user.tutor_profile.id
            else:
                return jsonify({"error": "Tutor profile not found for this user"}), 404
        elif user.role == 'admin':
            role_id = 0 # Admin role doesn't have a separate profile record currently
        
        return jsonify({
            "message": "Login successful",
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "role_id": role_id
        }), 200

    return jsonify({"error": "Invalid email or password"}), 401

@main.route('/api/profile/<int:student_id>', methods=['PUT', 'GET'])
@main.route('/api/profile/student/<int:student_id>', methods=['PUT', 'GET'])
def student_profile(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    if request.method == 'PUT':
        data = request.get_json()
        student.interests = data.get('interests', student.interests)
        student.class_level = data.get('class_level', student.class_level)
        student.phone = data.get('phone', student.phone)
        student.profile_picture = data.get('profile_picture', student.profile_picture)
        
        if 'name' in data:
            student.user.name = data['name']
        if 'email' in data:
            student.user.email = data['email']
            
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"})

    return jsonify({
        "id": student.id,
        "name": student.user.name,
        "email": student.user.email,
        "phone": student.phone or "",
        "interests": student.interests or "",
        "class_level": student.class_level or "",
        "profile_picture": student.profile_picture or ""
    })

@main.route('/api/search_tutors', methods=['GET'])
@main.route('/api/tutors/search', methods=['GET'])
def search_tutors():
    query = request.args.get('query') or request.args.get('q') or ''
    query = query.strip()
    
    # 1. Fetch all tutors with associated User data
    all_tutors = Tutor.query.join(User).all()
    
    tutor_data_list = []
    for t in all_tutors:
        tutor_data_list.append({
            "id": t.id,
            "name": t.user.name,
            "subjects": t.subjects or "",
            "rating": t.rating,
            "experience": t.experience
        })

    if not query:
        # Return all tutors sorted by rating if no query
        results = sorted(tutor_data_list, key=lambda x: x['rating'], reverse=True)
        return jsonify(results), 200

    # 2. Key-word / ilike Filtering (PostgreSQL optimized concept)
    # ilike is handled by SQLAlchemy's .ilike() but since we already have the list, 
    # we simulate the intelligent ranking here.
    match_results = []
    q_lower = query.lower()
    
    for t in tutor_data_list:
        name = t['name'].lower()
        subjects = t['subjects'].lower()
        
        relevance = 0
        if q_lower in name: relevance += 10
        if q_lower in subjects: relevance += 5
        
        # Fuzzy check for specific keywords
        subject_list = [s.strip().lower() for s in subjects.split(',')]
        if any(difflib.SequenceMatcher(None, q_lower, s).ratio() > 0.7 for s in subject_list):
            relevance += 3

        if relevance > 0:
            res = t.copy()
            # Ranking logic: relevance + rating
            res['relevance_score'] = relevance + t['rating']
            res['suggestion'] = f"{t['name']} - {(t['subjects'].split(',')[0])}"
            match_results.append(res)

    # 3. Final Ranking
    match_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return jsonify(match_results), 200

@main.route('/api/top_tutors', methods=['GET'])
def get_top_tutors():
    # Sort by rating descending, limit to 6
    top_tutors = Tutor.query.join(User).order_by(Tutor.rating.desc()).limit(6).all()
    results = []
    for t in top_tutors:
        results.append({
            "id": t.id,
            "name": t.user.name,
            "subjects": t.subjects or "",
            "rating": t.rating,
            "experience": t.experience
        })
    return jsonify(results), 200

@main.route('/api/my_tutors/<int:student_id>', methods=['GET'])
def get_my_tutors(student_id):
    # Fetch tutors from previous bookings
    previous_tutors = Tutor.query.join(Schedule).filter(Schedule.student_id == student_id).distinct().all()
    results = []
    for t in previous_tutors:
        results.append({
            "id": t.id,
            "name": t.user.name,
            "subjects": t.subjects,
            "rating": t.rating
        })
    return jsonify(results), 200

@main.route('/api/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    other_id = request.args.get('other_id', type=int)
    
    if other_id:
        # Fetch messages between specific pair
        messages = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_id)) |
            ((Message.sender_id == other_id) & (Message.receiver_id == user_id))
        ).order_by(Message.timestamp.asc()).all()
    else:
        # Fetch messages where the user is either sender or receiver
        messages = Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).order_by(Message.timestamp.asc()).all()
    
    results = []
    for msg in messages:
        sender_name = msg.sender.name
        if msg.sender_id == user_id:
            sender_name += " (You)"
        results.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "sender_name": sender_name,
            "message": msg.content,
            "file_url": msg.file_url,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(results), 200

@main.route('/api/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    file_url = data.get('file_url')

    if not all([sender_id, receiver_id]) or (not content and not file_url):
        return jsonify({"error": "Missing message details"}), 400

    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content or "", file_url=file_url)
    db.session.add(message)
    
    # Trigger notification for receiver
    sender = User.query.get(sender_id)
    notif_text = content[:30] if content else "Sent a file"
    notification = Notification(user_id=receiver_id, message=f"New message from {sender.name}: {notif_text}...")
    db.session.add(notification)
    
    db.session.commit()
    return jsonify({"message": "Message sent"}), 201

@main.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid collisions
        from datetime import datetime
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        file_url = f"uploads/messaging/{filename}"
        return jsonify({"message": "File uploaded successfully", "file_url": file_url}), 200
    return jsonify({"error": "File type not allowed"}), 400

@main.route('/book_session', methods=['POST'])
@main.route('/api/schedule/book', methods=['POST'])
def book_session():
    data = request.get_json()
    student_id = data.get('student_id')
    tutor_id = data.get('tutor_id')
    subject = data.get('subject')
    date = data.get('date')
    time = data.get('time')

    if not all([student_id, tutor_id, subject, date, time]):
        return jsonify({"error": "Missing booking details"}), 400

    # Conflict Check: Is the tutor already booked at this exact time?
    existing_session = Schedule.query.filter_by(tutor_id=tutor_id, date=date, time=time).first()
    if existing_session:
        return jsonify({"error": "Tutor is already booked at this time. Please choose another slot."}), 409

    session = Schedule(student_id=student_id, tutor_id=tutor_id, subject=subject, date=date, time=time)
    db.session.add(session)
    
    # Trigger notification for tutor
    student = Student.query.get(student_id)
    tutor = Tutor.query.get(tutor_id)
    if student and tutor:
        # Simulate Email Notification
        print(f"--- EMAIL SENT TO {tutor.user.email} ---")
        print(f"Subject: New Booking from {student.user.name}")
        print(f"Message: You have a new booking for {subject} on {date} at {time}.")
        print(f"---------------------------------------")
        
        notification = Notification(
            user_id=tutor.user_id, 
            message=f"New booking from {student.user.name} for {subject} on {date} at {time}"
        )
        db.session.add(notification)
        
    db.session.commit()
    return jsonify({"message": "Session booked successfully", "id": session.id}), 201

@main.route('/api/tutor/availability', methods=['PUT'])
def update_availability():
    data = request.get_json()
    tutor_id = data.get('tutor_id')
    availability = data.get('availability_info')

    if not tutor_id or availability is None:
        return jsonify({"error": "Missing tutor_id or availability_info"}), 400

    tutor = Tutor.query.get(tutor_id)
    if not tutor:
        return jsonify({"error": "Tutor not found"}), 404

    tutor.availability_info = availability
    db.session.commit()
    return jsonify({"message": "Availability updated successfully"}), 200

@main.route('/api/schedules/<int:student_id>', methods=['GET'])
@main.route('/api/schedule/student/<int:student_id>', methods=['GET'])
def get_student_schedule(student_id):
    sessions = Schedule.query.filter_by(student_id=student_id).all()
    results = []
    for s in sessions:
        results.append({
            "id": s.id,
            "tutor_id": s.tutor_id,
            "tutor_user_id": s.tutor.user_id,
            "tutor_name": s.tutor.user.name,
            "subject": s.subject,
            "date": s.date,
            "time": s.time,
            "status": s.status,
            "meeting_link": s.meeting_link or f"https://meet.jit.si/teach2learn-{s.id}"
        })
    return jsonify(results), 200

@main.route('/api/schedules/tutor/<int:tutor_id>', methods=['GET'])
def get_tutor_schedule(tutor_id):
    sessions = Schedule.query.filter_by(tutor_id=tutor_id).all()
    results = []
    for s in sessions:
        results.append({
            "id": s.id,
            "student_id": s.student_id,
            "student_user_id": s.student.user_id,
            "student_name": s.student.user.name,
            "subject": s.subject,
            "date": s.date,
            "time": s.time,
            "status": s.status,
            "meeting_link": s.meeting_link or f"https://meet.jit.si/teach2learn-{s.id}"
        })
    return jsonify(results), 200

@main.route('/api/profile/tutor/<int:tutor_id>', methods=['PUT', 'GET'])
def tutor_profile(tutor_id):
    tutor = Tutor.query.get(tutor_id)
    if not tutor:
        return jsonify({"error": "Tutor not found"}), 404

    if request.method == 'PUT':
        data = request.get_json()
        tutor.subjects = data.get('subjects', tutor.subjects)
        tutor.experience = data.get('experience', tutor.experience)
        
        if 'name' in data:
            tutor.user.name = data['name']
        if 'email' in data:
            tutor.user.email = data['email']
            
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"})

    return jsonify({
        "id": tutor.id,
        "name": tutor.user.name,
        "email": tutor.user.email,
        "subjects": tutor.subjects or "",
        "experience": tutor.experience or "",
        "rating": tutor.rating
    })

@main.route('/api/real_messages/<int:user_id>', methods=['GET'])
def get_user_messages(user_id):
    messages = Message.query.filter((Message.sender_id == user_id) | (Message.receiver_id == user_id)).order_by(Message.timestamp).all()
    results = []
    for m in messages:
        results.append({
            "sender": m.sender.name,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        })
    return jsonify(results), 200

@main.route('/api/feedback', methods=['POST'])
def submit_feedback():
# ... (existing feedback implementation remains similar but ensure it's here)
    data = request.get_json()
    student_id = data.get('student_id')
    tutor_id = data.get('tutor_id')
    rating = data.get('rating')
    comment = data.get('comment', "")
    
    if not all([student_id, tutor_id, rating]):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError
    except ValueError:
        return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

    student_skill_level = data.get('student_skill_level')

    feedback = Feedback(student_id=student_id, tutor_id=tutor_id, rating=rating, comment=comment, student_skill_level=student_skill_level)
    db.session.add(feedback)
    tutor = Tutor.query.get(tutor_id)
    if tutor:
        db.session.flush()
        feedbacks = Feedback.query.filter_by(tutor_id=tutor_id).all()
        if feedbacks:
            tutor.rating = sum(f.rating for f in feedbacks) / len(feedbacks)
    db.session.commit()
    return jsonify({"message": "Feedback submitted successfully"}), 201

@main.route('/api/recommend_tutors/<int:student_id>', methods=['GET'])
@main.route('/api/top_picks/lectures', methods=['GET']) # Backward compat
def recommend_tutors_upgraded(student_id=None):
    if student_id is None:
        student_id = request.args.get('student_id', type=int)
        
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
        
    query = request.args.get('subject')
    if not query:
        query = student.interests or "general learning"
        
    from models import StudentSubjectLevel
    skill_level_record = StudentSubjectLevel.query.filter_by(student_id=student_id, subject=query).first()
    student_skill_level = skill_level_record.skill_level if skill_level_record else None

    # Fetch all tutors for engine
    all_tutors = Tutor.query.join(User).all()
    tutor_data = []
    for t in all_tutors:
        # Calculate skill-based rating if student_skill_level is provided
        skill_rating = None
        if student_skill_level:
            skill_feedbacks = Feedback.query.filter_by(tutor_id=t.id, student_skill_level=student_skill_level).all()
            if skill_feedbacks:
                skill_rating = sum(f.rating for f in skill_feedbacks) / len(skill_feedbacks)

        tutor_data.append({
            "id": t.id,
            "name": t.user.name,
            "subjects": t.subjects or "",
            "rating": t.rating,
            "rating_from_same_skill_level_students": skill_rating
        })

    engine = RecommendationEngine(tutors=tutor_data)
    results = engine.recommend_tutors(query, student_skill_level=student_skill_level, top_n=3)
    
    return jsonify({
        "model_type": "Deep Learning Autoencoder",
        "recommendations": results,
        "is_top_picks": True
    }), 200

@main.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    results = []
    for n in notifications:
        results.append({
            "id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(results), 200

@main.route('/api/notifications/read/<int:notif_id>', methods=['POST'])
def mark_notification_read(notif_id):
    notification = Notification.query.get(notif_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    notification.is_read = True
    db.session.commit()
    return jsonify({"message": "Marked as read"}), 200

@main.route('/api/student/skill-level', methods=['POST'])
def update_student_skill_level():
    data = request.get_json()
    student_id = data.get('student_id')
    subject = data.get('subject')
    skill_level = data.get('skill_level')

    if not all([student_id, subject, skill_level]):
        return jsonify({"error": "Missing required fields"}), 400

    from models import StudentSubjectLevel
    # Check if a record already exists
    existing_level = StudentSubjectLevel.query.filter_by(student_id=student_id, subject=subject).first()
    if existing_level:
        existing_level.skill_level = skill_level
    else:
        new_level = StudentSubjectLevel(student_id=student_id, subject=subject, skill_level=skill_level)
        db.session.add(new_level)

    db.session.commit()
    return jsonify({"message": "Skill level updated successfully"}), 200

@main.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    users = User.query.all()
    results = []
    for u in users:
        results.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role
        })
    return jsonify(results), 200

@main.route('/api/admin/feedback', methods=['GET'])
def admin_get_feedback():
    feedbacks = Feedback.query.all()
    results = []
    for f in feedbacks:
        results.append({
            "id": f.id,
            "student_name": f.student.user.name if f.student else "Unknown",
            "tutor_name": f.tutor.user.name if f.tutor else "Unknown",
            "rating": f.rating,
            "comment": f.comment,
            "skill_level": f.student_skill_level
        })
    return jsonify(results), 200

@main.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_remove_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Simple check to prevent deleting the primary admin
    if user.email == "admin@teach2learn.com":
        return jsonify({"error": "Primary administrator cannot be removed"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user.name} removed successfully"}), 200

@main.route('/api/schedule/complete/<int:session_id>', methods=['PUT', 'POST'])
def complete_session(session_id):
    session = Schedule.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
        
    session.status = 'completed'
    db.session.commit()
    return jsonify({"message": "Session marked as completed"}), 200
