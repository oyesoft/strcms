import sqlite3
import os

# ---------------- Database Setup ----------------
DB_FILE = "data/lms.db"
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def get_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def setup_db():
    """Create all tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Lessons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            title TEXT NOT NULL,
            video_url TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')

    # Enrollments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')

    # Progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            lesson_id INTEGER,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(lesson_id) REFERENCES lessons(id)
        )
    ''')

    conn.commit()
    conn.close()

# ---------------- User Functions ----------------
def add_user(username, password, role="student"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, password, role))
    conn.commit()
    conn.close()

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ---------------- Course Functions ----------------
def add_course(title, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO courses (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    conn.close()

def get_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description FROM courses")
    courses = cursor.fetchall()
    conn.close()
    return courses

def enroll_course(user_id, course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM enrollments WHERE user_id=? AND course_id=?", (user_id, course_id))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (user_id, course_id))
        conn.commit()
    conn.close()

def get_enrolled_courses(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT courses.id, courses.title, courses.description
        FROM courses
        JOIN enrollments ON courses.id = enrollments.course_id
        WHERE enrollments.user_id=?
    ''', (user_id,))
    courses = cursor.fetchall()
    conn.close()
    return courses

# ---------------- Lesson Functions ----------------
def add_lesson(course_id, title, video_url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lessons (course_id, title, video_url) VALUES (?, ?, ?)",
                   (course_id, title, video_url))
    conn.commit()
    conn.close()

def get_lessons(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, video_url FROM lessons WHERE course_id=?", (course_id,))
    lessons = cursor.fetchall()
    conn.close()
    return lessons

# ---------------- Delete Lesson ----------------
def delete_lesson(lesson_id):
    """Delete a lesson by its ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
    conn.commit()
    conn.close()

# ---------------- Progress Functions ----------------
def mark_lesson_completed(user_id, lesson_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM progress WHERE user_id=? AND lesson_id=?", (user_id, lesson_id))
    if cursor.fetchone():
        cursor.execute("UPDATE progress SET completed=1 WHERE user_id=? AND lesson_id=?", (user_id, lesson_id))
    else:
        cursor.execute("INSERT INTO progress (user_id, lesson_id, completed) VALUES (?, ?, 1)", (user_id, lesson_id))
    conn.commit()
    conn.close()

def get_lesson_progress(user_id, lesson_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT completed FROM progress WHERE user_id=? AND lesson_id=?", (user_id, lesson_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# ---------------- Initialize Database ----------------
setup_db()
