from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import csv
import os

app = Flask(__name__, template_folder='ui', static_folder='ui')
CORS(app)

# Database setup
DATABASE = 'bookings.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create timetable table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            room TEXT NOT NULL,
            faculty TEXT NOT NULL,
            subject TEXT NOT NULL,
            semester TEXT NOT NULL
        )
    ''')
    
    # Create bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty TEXT NOT NULL,
            faculty_name TEXT,
            room TEXT NOT NULL,
            subject TEXT,
            purpose TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'pending',
            timestamp TEXT NOT NULL,
            approved_at TEXT,
            rejected_at TEXT
        )
    ''')
    
    # Insert default HOD user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('deveshsir@geu.ac.in',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (email, password, role, name, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('deveshsir@geu.ac.in', 'qwerty123', 'hod', 'Dr. Devesh', datetime.now().isoformat()))
        print("✅ Default HOD user created: deveshsir@geu.ac.in")
    
    conn.commit()
    conn.close()

def load_timetable_from_csv():
    """Load timetable from CSV file into database"""
    csv_path = 'data/timetable.csv'
    
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clear existing timetable
    cursor.execute('DELETE FROM timetable')
    
    # Load from CSV
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Convert 12-hour time format to 24-hour format
            time_str = row.get('Time', '')
            if time_str:
                # Handle formats like "01:00-02:00" -> "13:00-14:00"
                parts = time_str.split('-')
                if len(parts) == 2:
                    start, end = parts
                    start_hour = int(start.split(':')[0])
                    end_hour = int(end.split(':')[0])
                    
                    # Convert PM times (01:00-05:00 PM are 13:00-17:00)
                    if start_hour >= 1 and start_hour <= 5 and 'PM' not in time_str:
                        # Check if it's afternoon time (after 12:00)
                        if start_hour < 8:  # Times like 01:00, 02:00 are afternoon
                            start_hour += 12
                            end_hour += 12
                    
                    time_str = f"{start_hour:02d}:{start.split(':')[1]}-{end_hour:02d}:{end.split(':')[1]}"
            
            cursor.execute('''
                INSERT INTO timetable (day, time, room, faculty, subject, semester)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row.get('Day', ''),
                time_str,
                row.get('Room', ''),
                row.get('Faculty', ''),
                row.get('Subject', ''),
                row.get('Semester', '')
            ))
    
    conn.commit()
    count = cursor.execute('SELECT COUNT(*) FROM timetable').fetchone()[0]
    conn.close()
    
    print(f"✅ Timetable loaded successfully ({count} entries)")

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Serve frontend HTML"""
    return render_template('frontend.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (images, etc.)"""
    return send_from_directory('ui', filename)

@app.route('/api/login', methods=['POST'])
def login():
    """Validate user login"""
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')
    role = data.get('role', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # For HOD, validate against database
    if role == 'hod':
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ? AND role = ?', 
                      (email, password, 'hod'))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'email': user['email'],
                    'role': user['role'],
                    'name': user['name']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
    
    elif role == 'faculty':
        if email and '@' in email:
            # Check if faculty exists, if not create entry
            cursor.execute('SELECT * FROM users WHERE email = ? AND role = ?', (email, 'faculty'))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute('''
                    INSERT INTO users (email, password, role, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (email, '', 'faculty', datetime.now().isoformat()))
                conn.commit()
            
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'email': email,
                    'role': 'faculty'
                }
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 401
    
    conn.close()
    return jsonify({
        'success': False,
        'message': 'Invalid role'
    }), 400

@app.route('/api/faculty', methods=['GET'])
def get_faculty():
    """Get all unique faculty names from timetable"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT faculty FROM timetable ORDER BY faculty')
    rows = cursor.fetchall()
    
    faculty_list = [row['faculty'] for row in rows]
    conn.close()
    return jsonify(faculty_list)

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all unique rooms from timetable"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT room FROM timetable ORDER BY room')
    rows = cursor.fetchall()
    
    rooms = []
    for row in rows:
        room_name = row['room']
        # Determine room type and capacity based on prefix
        if room_name.startswith('A') or room_name.startswith('B'):
            room_type = 'Classroom'
            capacity = '60 Students'
        elif room_name.startswith('Lab'):
            room_type = 'Computer Lab'
            capacity = '35 Systems'
        elif room_name.startswith('Seminar'):
            room_type = 'Seminar Hall'
            capacity = '100 People'
        elif room_name.startswith('LT'):
            room_type = 'Lecture Theatre'
            capacity = '80 Students'
        else:
            room_type = 'Room'
            capacity = 'Various'
        
        rooms.append({
            'id': room_name,
            'type': room_type,
            'capacity': capacity
        })
    
    conn.close()
    return jsonify(rooms)

@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    """Get full timetable"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM timetable')
    rows = cursor.fetchall()
    
    timetable = [{
        'day': row['day'],
        'time': row['time'],
        'room': row['room'],
        'faculty': row['faculty'],
        'subject': row['subject'],
        'semester': row['semester']
    } for row in rows]
    
    conn.close()
    return jsonify(timetable)

@app.route('/api/empty', methods=['GET'])
def get_empty_rooms():
    """Check available rooms for given day and time"""
    day = request.args.get('day', '')
    time = request.args.get('time', '')
    
    all_rooms = ['C-101', 'L-201', 'SH-301']
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT room FROM timetable 
        WHERE day = ? AND time = ?
    ''', (day, time))
    
    occupied = [row['room'] for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT DISTINCT room FROM bookings 
        WHERE status = 'approved' 
        AND datetime(start_time) <= datetime(?)
        AND datetime(end_time) >= datetime(?)
    ''', (f"{day} {time}", f"{day} {time}"))
    
    booked = [row['room'] for row in cursor.fetchall()]
    
    conn.close()
    
    occupied_rooms = set(occupied + booked)
    empty_rooms = [room for room in all_rooms if room not in occupied_rooms]
    
    return jsonify({'empty_rooms': empty_rooms})

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings"""
    faculty = request.args.get('faculty')
    status = request.args.get('status')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM bookings'
    params = []
    
    conditions = []
    if faculty:
        conditions.append('faculty = ?')
        params.append(faculty)
    if status:
        conditions.append('status = ?')
        params.append(status)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY id DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    bookings = [{
        'id': row['id'],
        'faculty': row['faculty'],
        'facultyName': row['faculty_name'] if 'faculty_name' in row.keys() else '',
        'subject': row['subject'] if 'subject' in row.keys() else '',
        'room': row['room'],
        'purpose': row['purpose'],
        'start': row['start_time'],
        'end': row['end_time'],
        'notes': row['notes'],
        'status': row['status'],
        'timestamp': row['timestamp'],
        'approvedAt': row['approved_at'],
        'rejectedAt': row['rejected_at']
    } for row in rows]
    
    conn.close()
    return jsonify(bookings)

@app.route('/api/request', methods=['POST'])
def create_booking():
    """Create new booking request"""
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO bookings (faculty, faculty_name, room, subject, purpose, start_time, end_time, notes, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    ''', (
        data['faculty'],
        data.get('facultyName', ''),
        data['room'],
        data.get('subject', ''),
        data['purpose'],
        data['start'],
        data['end'],
        data.get('notes', ''),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'id': booking_id,
        'message': 'Booking request submitted successfully'
    })

@app.route('/api/approve/<int:booking_id>', methods=['POST'])
def approve_booking(booking_id):
    """Approve a booking request"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE bookings 
        SET status = 'approved', approved_at = ?
        WHERE id = ?
    ''', (datetime.now().isoformat(), booking_id))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'message': f"Booking for {row['room']} has been approved"
        })
    else:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

@app.route('/api/reject/<int:booking_id>', methods=['POST'])
def reject_booking(booking_id):
    """Reject a booking request"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE bookings 
        SET status = 'rejected', rejected_at = ?
        WHERE id = ?
    ''', (datetime.now().isoformat(), booking_id))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'message': f"Booking for {row['room']} has been rejected"
        })
    else:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404

if __name__ == '__main__':
    print("🌐 GEU Smart Classroom Booking System ")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Load timetable from CSV
    load_timetable_from_csv()
    
    print("=" * 60)
    print("Server starting on http://localhost:8080")
    print("=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)