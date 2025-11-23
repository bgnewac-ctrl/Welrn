from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import base64

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Simple file-based database
DB_FILE = 'welearn_data.json'
UPLOAD_FOLDER = 'uploads/notes'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Admin credentials
ADMIN_CREDENTIALS = {
    'username': 'Founder',
    'password': 'Admin@1000'
}

# Anna University Engineering Courses
ANNA_UNIVERSITY_COURSES = {
    "CSE": "Computer Science and Engineering",
    "IT": "Information Technology", 
    "ECE": "Electronics and Communication Engineering",
    "EEE": "Electrical and Electronics Engineering",
    "MECH": "Mechanical Engineering",
    "CIVIL": "Civil Engineering",
    "AERO": "Aeronautical Engineering",
    "AUTO": "Automobile Engineering",
    "PROD": "Production Engineering",
    "MCT": "Mechatronics Engineering",
    "BIOMED": "Biomedical Engineering",
    "BIOTECH": "Biotechnology",
    "CHEM": "Chemical Engineering",
    "FOOD": "Food Technology",
    "AGRI": "Agricultural Engineering",
    "ENVI": "Environmental Engineering",
    "ICE": "Instrumentation and Control Engineering",
    "META": "Metallurgical Engineering",
    "MINING": "Mining Engineering",
    "PETRO": "Petroleum Engineering",
    "TEXTILE": "Textile Technology",
    "ARCH": "Architecture",
    "PLAN": "Planning"
}

# Common Subject Codes
SUBJECT_CODES = {
    "MA8151": "Engineering Mathematics I",
    "PH8151": "Engineering Physics",
    "CY8151": "Engineering Chemistry",
    "GE8151": "Problem Solving and Python Programming",
    "GE8152": "Engineering Graphics",
    "HS8151": "Communicative English",
    "GE8161": "Problem Solving and Python Programming Laboratory",
    "BS8161": "Physics and Chemistry Laboratory",
    "MA8251": "Engineering Mathematics II",
    "PH8251": "Materials Science",
    "BE8251": "Basic Electrical and Electronics Engineering",
    "GE8291": "Environmental Science and Engineering",
    "CS8251": "Programming in C",
    "GE8261": "Engineering Practices Laboratory",
    "CS8261": "C Programming Laboratory",
    "CS8391": "Data Structures",
    "CS8392": "Object Oriented Programming",
    "EC8393": "Fundamentals of Data Structures in C",
    "CS8491": "Computer Architecture",
    "CS8492": "Database Management Systems",
    "CS8451": "Design and Analysis of Algorithms",
    "CS8591": "Computer Networks",
    "CS8501": "Theory of Computation",
    "CS8691": "Artificial Intelligence",
    "CS8792": "Cryptography and Network Security",
    "IT8076": "Software Testing",
    "CS8080": "Internet of Things",
    "CS8091": "Big Data Analytics"
}

def init_db():
    if not os.path.exists(DB_FILE):
        data = {
            'users': [],
            'notes': [],
            'ratings': [],
            'comments': [],
            'accesses': [],
            'admin_logs': []  # Fixed: Added admin_logs to initial data
        }
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)

def read_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        init_db()
        return read_db()

def write_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def log_admin_action(action, details, user_id=None):
    db_data = read_db()
    
    # Ensure admin_logs exists
    if 'admin_logs' not in db_data:
        db_data['admin_logs'] = []
    
    log_entry = {
        'id': len(db_data['admin_logs']) + 1,
        'action': action,
        'details': details,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr or '127.0.0.1'
    }
    db_data['admin_logs'].append(log_entry)
    write_db(db_data)

# Initialize database
init_db()

# Serve frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# API Routes
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        
        if (data.get('username') == ADMIN_CREDENTIALS['username'] and 
            data.get('password') == ADMIN_CREDENTIALS['password']):
            
            log_admin_action('ADMIN_LOGIN', 'Admin logged into the system')
            
            return jsonify({
                'message': 'Admin login successful',
                'user': {
                    'id': 'admin',
                    'name': 'Administrator',
                    'username': ADMIN_CREDENTIALS['username'],
                    'role': 'admin'
                }
            })
        
        return jsonify({'message': 'Invalid admin credentials'}), 401
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    try:
        db_data = read_db()
        
        # Ensure all required fields exist
        if 'admin_logs' not in db_data:
            db_data['admin_logs'] = []
        if 'accesses' not in db_data:
            db_data['accesses'] = []
        
        # Get today's date
        today = datetime.now().date()
        
        # Filter today's activities
        def is_today(timestamp):
            try:
                if not timestamp:
                    return False
                activity_date = datetime.fromisoformat(timestamp).date()
                return activity_date == today
            except:
                return False
        
        # Today's registrations
        today_registrations = [
            user for user in db_data.get('users', []) 
            if is_today(user.get('created_at', ''))
        ]
        
        # Today's note uploads
        today_notes = [
            note for note in db_data.get('notes', []) 
            if is_today(note.get('created_at', ''))
        ]
        
        # Today's note accesses
        today_accesses = [
            access for access in db_data.get('accesses', []) 
            if is_today(access.get('accessed_at', ''))
        ]
        
        # Today's admin logs
        today_logs = [
            log for log in db_data.get('admin_logs', []) 
            if is_today(log.get('timestamp', ''))
        ]
        
        # Statistics
        total_users = len(db_data.get('users', []))
        total_notes = len(db_data.get('notes', []))
        total_professors = len([u for u in db_data.get('users', []) if u.get('is_professor', False)])
        total_downloads = sum(note.get('download_count', 0) for note in db_data.get('notes', []))
        
        # Course-wise distribution
        course_distribution = {}
        for user in db_data.get('users', []):
            course = user.get('course', 'Unknown')
            course_distribution[course] = course_distribution.get(course, 0) + 1
        
        # Recent activities (last 50 activities)
        recent_activities = []
        
        # Add user registrations
        for user in db_data.get('users', [])[-20:]:
            recent_activities.append({
                'type': 'USER_REGISTER',
                'user_name': user.get('name', 'Unknown'),
                'user_email': user.get('email', 'Unknown'),
                'course': user.get('course', 'N/A'),
                'timestamp': user.get('created_at', ''),
                'details': f"New { 'Professor' if user.get('is_professor') else 'Student' } registered: {user.get('name', 'Unknown')}"
            })
        
        # Add note uploads
        for note in db_data.get('notes', [])[-20:]:
            donor = next((u for u in db_data.get('users', []) if u['id'] == note['donor_id']), None)
            recent_activities.append({
                'type': 'NOTE_UPLOAD',
                'user_name': donor.get('name', 'Unknown') if donor else 'Unknown',
                'subject': note.get('subject', 'Unknown'),
                'subject_code': note.get('subject_code', 'N/A'),
                'timestamp': note.get('created_at', ''),
                'details': f"New note uploaded: {note.get('title', 'Unknown')} ({note.get('subject_code', 'N/A')})"
            })
        
        # Add note accesses
        for access in db_data.get('accesses', [])[-20:]:
            user = next((u for u in db_data.get('users', []) if u['id'] == access['user_id']), None)
            note = next((n for n in db_data.get('notes', []) if n['id'] == access['note_id']), None)
            if user and note:
                recent_activities.append({
                    'type': 'NOTE_ACCESS',
                    'user_name': user.get('name', 'Unknown'),
                    'subject': note.get('subject', 'Unknown'),
                    'timestamp': access.get('accessed_at', ''),
                    'details': f"Note accessed: {note.get('title', 'Unknown')}"
                })
        
        # Add admin logs
        for log in db_data.get('admin_logs', [])[-20:]:
            recent_activities.append({
                'type': 'ADMIN_ACTION',
                'user_name': 'System',
                'timestamp': log.get('timestamp', ''),
                'details': f"Admin action: {log.get('action', 'Unknown')} - {log.get('details', '')}"
            })
        
        # Sort by timestamp and get latest
        recent_activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        recent_activities = recent_activities[:30]
        
        dashboard_data = {
            'overview': {
                'total_users': total_users,
                'total_notes': total_notes,
                'total_professors': total_professors,
                'total_downloads': total_downloads,
                'today_registrations': len(today_registrations),
                'today_uploads': len(today_notes),
                'today_downloads': len(today_accesses)
            },
            'today_activities': {
                'registrations': today_registrations,
                'uploads': today_notes,
                'accesses': today_accesses,
                'admin_logs': today_logs
            },
            'course_distribution': course_distribution,
            'recent_activities': recent_activities,
            'all_users': db_data.get('users', [])
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'message': f'Error loading admin dashboard: {str(e)}'}), 500

@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify(ANNA_UNIVERSITY_COURSES)

@app.route('/api/subject-codes', methods=['GET'])
def get_subject_codes():
    return jsonify(SUBJECT_CODES)

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        db_data = read_db()
        
        # Ensure users list exists
        if 'users' not in db_data:
            db_data['users'] = []
        
        # Check if user exists
        for user in db_data['users']:
            if user['email'] == data['email']:
                return jsonify({'message': 'Email already registered'}), 400
            if user['roll_number'] == data['roll_number']:
                return jsonify({'message': 'Roll number already registered'}), 400
        
        new_user = {
            'id': len(db_data['users']) + 1,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'roll_number': data['roll_number'],
            'course': data['course'],
            'course_duration': data['course_duration'],
            'password': data['password'],
            'is_professor': data.get('is_professor', False),
            'created_at': datetime.now().isoformat()
        }
        
        db_data['users'].append(new_user)
        write_db(db_data)
        
        # Log the registration
        user_type = "Professor" if new_user['is_professor'] else "Student"
        log_admin_action('USER_REGISTRATION', 
                        f"{user_type} registered: {new_user['name']} ({new_user['email']})",
                        new_user['id'])
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': new_user['id'],
                'name': new_user['name'],
                'email': new_user['email'],
                'roll_number': new_user['roll_number'],
                'course': new_user['course'],
                'is_professor': new_user['is_professor']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        db_data = read_db()
        
        # Ensure users list exists
        if 'users' not in db_data:
            db_data['users'] = []
            write_db(db_data)
            return jsonify({'message': 'Invalid credentials'}), 401
        
        for user in db_data['users']:
            if user['email'] == data['email'] and user['password'] == data['password']:
                # Log the login
                user_type = "Professor" if user['is_professor'] else "Student"
                log_admin_action('USER_LOGIN', 
                               f"{user_type} logged in: {user['name']} ({user['email']})",
                               user['id'])
                
                return jsonify({
                    'message': 'Login successful',
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email'],
                        'roll_number': user['roll_number'],
                        'course': user['course'],
                        'is_professor': user['is_professor'],
                        'role': 'professor' if user['is_professor'] else 'student'
                    }
                })
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/notes', methods=['POST'])
def upload_note():
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            filename = f"{int(datetime.now().timestamp())}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            db_data = read_db()
            
            # Ensure notes list exists
            if 'notes' not in db_data:
                db_data['notes'] = []
            
            new_note = {
                'id': len(db_data['notes']) + 1,
                'title': request.form.get('title'),
                'description': request.form.get('description'),
                'subject': request.form.get('subject'),
                'subject_code': request.form.get('subject_code'),
                'course': request.form.get('course'),
                'semester': int(request.form.get('semester')),
                'file_path': file_path,
                'is_professional': request.form.get('is_professional') == 'true',
                'price': float(request.form.get('price', 0)),
                'donor_id': int(request.form.get('donor_id')),
                'avg_rating': 0.0,
                'download_count': 0,
                'created_at': datetime.now().isoformat()
            }
            
            db_data['notes'].append(new_note)
            write_db(db_data)
            
            # Log the note upload
            donor = next((u for u in db_data.get('users', []) if u['id'] == new_note['donor_id']), None)
            if donor:
                log_admin_action('NOTE_UPLOAD', 
                               f"Note uploaded by {donor['name']}: {new_note['title']} ({new_note['subject_code']})",
                               donor['id'])
            
            return jsonify({'message': 'Note uploaded successfully', 'note_id': new_note['id']}), 201
        
        return jsonify({'message': 'Only PDF files allowed'}), 400
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        db_data = read_db()
        course = request.args.get('course')
        semester = request.args.get('semester')
        subject = request.args.get('subject')
        subject_code = request.args.get('subject_code')
        search = request.args.get('search')
        
        notes = db_data.get('notes', [])
        
        # Filter notes
        if course:
            notes = [n for n in notes if n['course'] == course]
        if semester:
            notes = [n for n in notes if n['semester'] == int(semester)]
        if subject:
            notes = [n for n in notes if subject.lower() in n['subject'].lower()]
        if subject_code:
            notes = [n for n in notes if subject_code.upper() in n.get('subject_code', '').upper()]
        if search:
            notes = [n for n in notes if (
                search.lower() in n['subject'].lower() or 
                search.upper() in n.get('subject_code', '').upper() or
                search.lower() in n['title'].lower()
            )]
        
        # Add donor names
        users = {user['id']: user for user in db_data.get('users', [])}
        for note in notes:
            donor = users.get(note['donor_id'], {})
            note['donor_name'] = donor.get('name', 'Unknown')
        
        return jsonify(notes)
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/notes/<int:note_id>/view', methods=['GET'])
def view_note(note_id):
    try:
        db_data = read_db()
        note = next((n for n in db_data.get('notes', []) if n['id'] == note_id), None)
        
        if not note:
            return jsonify({'message': 'Note not found'}), 404
        
        user_id = request.args.get('user_id', type=int)
        if user_id:
            # Ensure accesses list exists
            if 'accesses' not in db_data:
                db_data['accesses'] = []
            
            # Record access
            new_access = {
                'id': len(db_data['accesses']) + 1,
                'user_id': user_id,
                'note_id': note_id,
                'accessed_at': datetime.now().isoformat()
            }
            db_data['accesses'].append(new_access)
            
            # Update download count
            note['download_count'] += 1
            write_db(db_data)
            
            # Log the note access
            user = next((u for u in db_data.get('users', []) if u['id'] == user_id), None)
            if user:
                log_admin_action('NOTE_ACCESS', 
                               f"Note accessed by {user['name']}: {note['title']}",
                               user['id'])
        
        return send_file(note['file_path'], as_attachment=False)
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/user/dashboard', methods=['GET'])
def user_dashboard():
    try:
        user_id = request.args.get('user_id', type=int)
        db_data = read_db()
        
        user = next((u for u in db_data.get('users', []) if u['id'] == user_id), None)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        donated_notes = [n for n in db_data.get('notes', []) if n['donor_id'] == user_id]
        received_accesses = [a for a in db_data.get('accesses', []) if a['user_id'] == user_id]
        
        # Add note details to received notes
        notes_dict = {n['id']: n for n in db_data.get('notes', [])}
        received_notes = []
        for access in received_accesses[-10:]:
            note = notes_dict.get(access['note_id'])
            if note:
                received_notes.append({
                    'id': access['id'],
                    'title': note['title'],
                    'subject': note['subject'],
                    'subject_code': note.get('subject_code', ''),
                    'accessed_at': access['accessed_at']
                })
        
        dashboard_data = {
            'user': {
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'roll_number': user['roll_number'],
                'course': user['course'],
                'course_duration': user['course_duration']
            },
            'donated_notes': [
                {
                    'id': note['id'],
                    'title': note['title'],
                    'subject': note['subject'],
                    'subject_code': note.get('subject_code', ''),
                    'avg_rating': note['avg_rating'],
                    'download_count': note['download_count'],
                    'created_at': note['created_at']
                } for note in donated_notes
            ],
            'received_notes': received_notes
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({'message': 'API is working!'})

if __name__ == '__main__':
    print("WeLearn Server Starting...")
    print("Access the application at: http://127.0.0.1:5000")
    print("Admin Login: Username: Founder, Password: Admin@1000")
    print("To access from other devices, use your phone's IP address")
    app.run(host='0.0.0.0', port=5000, debug=True)