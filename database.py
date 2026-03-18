import sqlite3
from sqlite3 import Connection

DB_FILE = "data/lms.db"

def get_connection() -> Connection:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def setup_db():
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

    # Enrollment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')

    conn.commit()
    conn.close()

def add_user(username, password, role="student"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user  # returns (id, role) or None

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

# Initialize DB on import
setup_db()
