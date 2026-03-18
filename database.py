import sqlite3
import bcrypt

DB_FILE = "lms.db"


# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- USER FUNCTIONS ----------------
def add_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (username,password,role) VALUES (?,?,?)",
        (username, hashed.decode(), role)
    )

    conn.commit()
    conn.close()
    return True


def login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    if bcrypt.checkpw(password.encode(), user["password"].encode()):
        return dict(user)

    return None


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()
    return [dict(u) for u in users]


def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


def count_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    conn.close()
    return total


# ---------------- COURSE FUNCTIONS ----------------
def add_course(title, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO courses (title,description) VALUES (?,?)",
        (title, description)
    )

    conn.commit()
    conn.close()


def get_courses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses")
    rows = cursor.fetchall()

    conn.close()
    return [dict(r) for r in rows]


def count_courses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM courses")
    total = cursor.fetchone()[0]

    conn.close()
    return total


# ---------------- VIDEO FUNCTIONS ----------------
def fix_youtube_url(url):
    if "youtube.com/watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    return url


def add_video(course_id, title, url):

    if not title.strip():
        title = "Untitled Video"

    url = fix_youtube_url(url)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO videos (course_id,title,path) VALUES (?,?,?)",
        (course_id, title, url)
    )

    conn.commit()
    conn.close()


def get_videos(course_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title,path FROM videos WHERE course_id=?",
        (course_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {"title": r["title"], "path": r["path"]}
        for r in rows
    ]


# ---------------- FILE FUNCTIONS ----------------
def add_file(course_id, title, path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO files (course_id,title,path) VALUES (?,?,?)",
        (course_id, title, path)
    )

    conn.commit()
    conn.close()


def get_files(course_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title,path FROM files WHERE course_id=?",
        (course_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {"title": r["title"], "path": r["path"]}
        for r in rows
    ]


# ---------------- ENROLLMENT ----------------
def enroll(user_id, course_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM enrollments WHERE user_id=? AND course_id=?",
        (user_id, course_id)
    )

    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO enrollments (user_id,course_id) VALUES (?,?)",
            (user_id, course_id)
        )
        conn.commit()

    conn.close()


def get_enrollments(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT course_id FROM enrollments WHERE user_id=?",
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [r["course_id"] for r in rows]


def count_enrollments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM enrollments")
    total = cursor.fetchone()[0]

    conn.close()
    return total
