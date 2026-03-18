import sqlite3
import os

DB_FILE = "lms.db"

# Ensure DB exists
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Users
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")
    # Courses
    c.execute("""CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )""")
    # Videos
    c.execute("""CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        path TEXT
    )""")
    # Files
    c.execute("""CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        path TEXT
    )""")
    # Enrollments
    c.execute("""CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER
    )""")
    conn.commit()
    conn.close()

init_db()

# ---------------- USER FUNCTIONS ----------------
def add_user(username, password, role):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "role": row[3]}
    return None

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "username": r[1], "role": r[3]} for r in rows]

def delete_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# ---------------- COURSE FUNCTIONS ----------------
def add_course(title, desc):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO courses (title, description) VALUES (?, ?)", (title, desc))
    conn.commit()
    conn.close()

def get_courses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM courses")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2]} for r in rows]

# ---------------- VIDEO FUNCTIONS ----------------
def add_video(course_id, title, path):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO videos (course_id, title, path) VALUES (?, ?, ?)", (course_id, title, path))
    conn.commit()
    conn.close()

def get_videos(course_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE course_id=?", (course_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "course_id": r[1], "title": r[2], "path": r[3]} for r in rows]

# ---------------- FILE FUNCTIONS ----------------
def add_file(course_id, title, path):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO files (course_id, title, path) VALUES (?, ?, ?)", (course_id, title, path))
    conn.commit()
    conn.close()

def get_files(course_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM files WHERE course_id=?", (course_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "course_id": r[1], "title": r[2], "path": r[3]} for r in rows]

# ---------------- ENROLLMENTS ----------------
def enroll(user_id, course_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (user_id, course_id))
    conn.commit()
    conn.close()

def get_enrollments(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT course_id FROM enrollments WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# ---------------- ANALYTICS ----------------
def count_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def count_courses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM courses")
    count = c.fetchone()[0]
    conn.close()
    return count

def count_enrollments():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM enrollments")
    count = c.fetchone()[0]
    conn.close()
    return count
