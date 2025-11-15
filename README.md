# GEU Smart Classroom & Lab Booking System

A comprehensive web-based room booking and timetable management system for Graphic Era University, built with Flask (Python) backend and responsive Bootstrap frontend.

## Features

### Faculty Portal
- **Check Room Availability** - Real-time status of all classrooms, labs, and seminar halls
- **Weekly Calendar View** - Visual display of scheduled classes and approved bookings
- **Book Rooms** - Request bookings for various purposes (lectures, practicals, seminars, meetings) with subject and faculty name
- **My Bookings** - Track status of all submitted booking requests
- **Auto-refresh** - Updates every 5 seconds to sync with database

### HOD Dashboard
- **Pending Requests** - Review and manage incoming booking requests
- **Approve/Reject Bookings** - One-click approval or rejection with instant updates
- **Weekly Calendar** - View all scheduled classes and approved bookings
- **Booking History** - Complete record of all processed requests
- **Real-time Updates** - Synchronized data across all users

### System Features
- **Dynamic Room Loading** - Automatically fetches all rooms from timetable CSV
- **Smart Availability Checking** - Checks against both scheduled classes and approved bookings
- **Secure Authentication** - HOD login with validated credentials
- **Persistent Storage** - SQLite database for all bookings and user data
- **Responsive Design** - Modern UI with Bootstrap 5
- **Time Conflict Prevention** - Prevents double-booking of rooms

## Technology Stack

**Backend:**
- Python 3.x
- Flask 3.0.0
- Flask-CORS 4.0.0
- SQLite3

**Frontend:**
- HTML5
- CSS3
- JavaScript (ES6+)
- Bootstrap 5.3.3
- Font Awesome 6.4.0

## Project Structure

```
Dbms/
├── server.py                 # Flask backend server
├── requirements.txt          # Python dependencies
├── bookings.db              # SQLite database (auto-created)
├── data/
│   └── timetable.csv        # Class schedule data
└── ui/
    ├── frontend.html        # Main application interface
    └── geu1.jpg            # University logo/background
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   ###enter your github repo link
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Data Files**
   - Ensure `data/timetable.csv` exists with class schedule data
   - Format: `Day,Time,Room,Faculty,Subject,Semester`

4. **Run the Server**
   ```bash
   python server.py
   ```

5. **Access the Application**
   - Open your browser and navigate to: `http://localhost:8080`

## Login Credentials

### HOD Access
- **Email:** `deveshsir@geu.ac.in`
- **Password:** `qwerty123`
- **Role:** Head of Department (HOD)

### Faculty Access
- **Email:** Any valid email format (e.g., `faculty@geu.ac.in`)
- **Password:** Not required
- **Role:** Faculty

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique user email
- `password` - User password (HOD only)
- `role` - User role (faculty/hod)
- `name` - Display name
- `created_at` - Account creation timestamp

### Timetable Table
- `id` - Primary key
- `day` - Day of week
- `time` - Time slot (e.g., 09:00-10:00)
- `room` - Room ID
- `faculty` - Professor name
- `subject` - Course name
- `semester` - Class semester

### Bookings Table
- `id` - Primary key
- `faculty` - Faculty email
- `faculty_name` - Faculty member's name
- `room` - Room ID
- `subject` - Subject/Course name
- `purpose` - Booking purpose
- `start_time` - Booking start
- `end_time` - Booking end
- `notes` - Additional notes
- `status` - pending/approved/rejected
- `timestamp` - Request creation time
- `approved_at` - Approval timestamp
- `rejected_at` - Rejection timestamp

## Room Types

The system automatically categorizes rooms based on naming conventions:

- **A101, A102, B201, etc.** → Classroom (60 Students)
- **Lab1, Lab2, etc.** → Computer Lab (35 Systems)
- **Seminar1, Seminar2, etc.** → Seminar Hall (100 People)
- **LT-13, LT-15, etc.** → Lecture Theatre (80 Students)

## Timetable Format

CSV file should contain columns: `Day,Time,Room,Faculty,Subject,Semester`

Example:
```csv
Day,Time,Room,Faculty,Subject,Semester
Monday,09:00-10:00,A101,Dr. Mehta,Programming Fundamentals,BCA-1
Monday,10:00-11:00,A102,Prof. Gupta,Discrete Mathematics,BCA-1
Tuesday,09:00-10:00,Lab1,Dr. Iyer,Digital Logic Design,BCA-1
```

## API Endpoints

- `GET /` - Serve frontend application
- `POST /api/login` - User authentication
- `GET /api/faculty` - Get all faculty names from timetable
- `GET /api/rooms` - Get all available rooms
- `GET /api/timetable` - Get complete class schedule
- `GET /api/bookings` - Get all bookings (with filters)
- `POST /api/request` - Create new booking request
- `POST /api/approve/<id>` - Approve booking
- `POST /api/reject/<id>` - Reject booking

## Features in Detail

### Availability Status
- Available - Room is free
- Class Scheduled - Room has a scheduled class
- Booked - Room has an approved booking

### Calendar View
- Displays time slots from 8:00 AM to 6:00 PM
- Shows weekdays: Monday to Saturday
- Color-coded entries:
  - **Blue border** - Scheduled classes from timetable
  - **Green border** - Approved bookings

### Auto-Refresh
- Student view: Updates bookings and availability every 5 seconds
- HOD view: Updates pending requests and history every 5 seconds

## Troubleshooting

**Port Already in Use:**
```bash
# Find process using port 8080
netstat -ano | findstr :8080
# Kill the process (use PID from above)
taskkill /PID <PID> /F
```

**Database Issues:**
- Delete `bookings.db` file to reset database
- Server will recreate tables on next startup

**Module Not Found:**
```bash
pip install --upgrade -r requirements.txt
```

## Usage Workflow

### For Faculty:
1. Log in with university email
2. Select your name from the dropdown
3. Enter subject name for the class
4. Check room availability in real-time
5. View weekly calendar for scheduled classes
6. Submit booking request with details
7. Monitor request status in "My Bookings"

### For HOD:
1. Log in with HOD credentials
2. Review pending booking requests
3. Approve or reject requests with one click
4. View complete booking history
5. Monitor weekly calendar for all activities

## Security Features

- HOD login requires valid credentials stored in database
- Password validation for administrative access
- Session-based user management
- Input validation on all forms
- CORS enabled for secure cross-origin requests


## License

This project is developed for Graphic Era University's internal use.

---

**Developed for:** Your spideyguy Arsh  
**System:** Smart Classroom & Lab Management System  
**Version:** 1.0.0
