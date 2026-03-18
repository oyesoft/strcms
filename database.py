import os
import sqlite3
import bcrypt

# ---------------- PERSISTENT DATABASE SETUP ----------------
DB_FOLDER = "streamlit_data"
os.makedirs(DB_FOLDER, exist_ok=True)
DB_NAME = os.path.join(DB_FOLDER, "lms.db")


# ---------------- DATABASE CONNECTION ----------------
def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS videos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        path TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS files(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        path TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS enrollments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


# Initialize DB automatically
init_db()


# ---------------- USER FUNCTIONS ----------------
def add_user(username, password, role):
    conn = connect()
    cur = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            (username, hashed_password, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login(username, password):
    conn = connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
    return None


def get_all_users():
    conn = connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    conn.close()
    return users


def delete_user(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def count_users():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count


# ---------------- COURSE FUNCTIONS ----------------
def add_course(title, description):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO courses(title,description) VALUES(?,?)", (title, description))
    conn.commit()
    conn.close()


def get_courses():
    conn = connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    conn.close()
    return courses


def count_courses():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM courses")
    count = cur.fetchone()[0]
    conn.close()
    return count


# ---------------- VIDEO FUNCTIONS ----------------
def add_video(course_id, title, path):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO videos(course_id,title,path) VALUES(?,?,?)", (course_id, title, path))
    conn.commit()
    conn.close()


def get_videos(course_id):
    conn = connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM videos WHERE course_id=?", (course_id,))
        videos = cur.fetchall()
        return videos
    except sqlite3.OperationalError as e:
        print("Database error in get_videos:", e)
        return []
    finally:
        conn.close()


# ---------------- FILE FUNCTIONS ----------------
def add_file(course_id, title, path):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO files(course_id,title,path) VALUES(?,?,?)", (course_id, title, path))
    conn.commit()
    conn.close()


def get_files(course_id):
    conn = connect()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM files WHERE course_id=?", (course_id,))
        files = cur.fetchall()
        return files
    except sqlite3.OperationalError as e:
        print("Database error in get_files:", e)
        return []
    finally:
        conn.close()


# ---------------- ENROLLMENT FUNCTIONS ----------------
def enroll(user_id, course_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO enrollments(user_id,course_id) VALUES(?,?)", (user_id, course_id))
    conn.commit()
    conn.close()


def get_enrollments(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT course_id FROM enrollments WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def count_enrollments():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM enrollments")
    count = cur.fetchone()[0]
    conn.close()
    return count
