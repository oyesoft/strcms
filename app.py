import streamlit as st
import database as db
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="LMS", layout="wide")
st.title("📚 Advanced LMS")

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.just_logged_out = False


# ---------------- LOGOUT ----------------
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.just_logged_out = True


# ---------------- LOGIN USER ----------------
def login_user(user):
    st.session_state.logged_in = True
    st.session_state.user_id = user["id"]
    st.session_state.username = user["username"]
    st.session_state.role = user["role"]


# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:

    if st.session_state.just_logged_out:
        st.info("Logged out successfully")
        st.session_state.just_logged_out = False

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    # ---------------- REGISTER ----------------
    if choice == "Register":
        st.subheader("Create Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["student", "admin"])

        if st.button("Register"):
            if username == "" or password == "":
                st.warning("Fill all fields")
            else:
                success = db.add_user(username, password, role)
                if success:
                    st.success("Account created. You can login.")
                else:
                    st.error("Username already exists")

    # ---------------- LOGIN ----------------
    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = db.login(username, password)
            if user:
                login_user(user)
                st.experimental_rerun()
            else:
                st.error("Invalid login details")


# ---------------- DASHBOARD ----------------
if st.session_state.logged_in:

    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.button("Logout", on_click=logout)

    role = st.session_state.role
    user_id = st.session_state.user_id

    st.info(f"Welcome {st.session_state.username}")

    # ---------------- ADMIN DASHBOARD ----------------
    if role == "admin":
        st.header("Admin Dashboard")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Courses", "Videos", "Files", "Analytics", "Users"]
        )

        # ---------------- COURSES ----------------
        with tab1:
            st.subheader("Add Course")
            title = st.text_input("Course Title")
            desc = st.text_area("Course Description")
            if st.button("Add Course"):
                if title == "" or desc == "":
                    st.warning("Enter title and description")
                else:
                    db.add_course(title, desc)
                    st.success("Course added")
            st.divider()

            st.subheader("All Courses")
            try:
                courses = db.get_courses()
                if not courses:
                    st.info("No courses yet")
                else:
                    for c in courses:
                        st.write(f"📘 {c['title']} - {c['description']}")
            except Exception as e:
                st.error(f"Error loading courses: {e}")

        # ---------------- VIDEOS ----------------
        with tab2:
            st.subheader("Add Course Video")
            try:
                courses = db.get_courses()
                if courses:
                    titles = [c["title"] for c in courses]
                    selected = st.selectbox("Course", titles)
                    video_title = st.text_input("Video Title")
                    video_url = st.text_input("YouTube URL")
                    if st.button("Add Video"):
                        course_id = next((c["id"] for c in courses if c["title"] == selected), None)
                        if not video_url:
                            st.warning("Enter YouTube URL")
                        else:
                            db.add_video(course_id, video_title, video_url)
                            st.success("Video added")
                else:
                    st.info("Create a course first")
            except Exception as e:
                st.error(f"Error loading courses/videos: {e}")

        # ---------------- FILES ----------------
        with tab3:
            st.subheader("Upload Course File")
            try:
                courses = db.get_courses()
                if courses:
                    titles = [c["title"] for c in courses]
                    selected = st.selectbox("Course", titles)
                    file_title = st.text_input("File Title")
                    uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])
                    if st.button("Upload File"):
                        if uploaded_file:
                            os.makedirs("files", exist_ok=True)
                            path = f"files/{uploaded_file.name}"
                            with open(path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            course_id = next((c["id"] for c in courses if c["title"] == selected), None)
                            db.add_file(course_id, file_title, path)
                            st.success("File uploaded")
                        else:
                            st.warning("Upload a file")
                else:
                    st.info("Create a course first")
            except Exception as e:
                st.error(f"Error uploading files: {e}")

        # ---------------- ANALYTICS ----------------
        with tab4:
            try:
                col1, col2, col3 = st.columns(3)
                col1.metric("Users", db.count_users())
                col2.metric("Courses", db.count_courses())
                col3.metric("Enrollments", db.count_enrollments())
            except Exception as e:
                st.error(f"Error loading analytics: {e}")

        # ---------------- USERS ----------------
        with tab5:
            try:
                users = db.get_all_users()
                for u in users:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    col1.write(u["username"])
                    col2.write(u["role"])
                    if col3.button("Delete", key=f"user{u['id']}"):
                        db.delete_user(u["id"])
                        st.success("User deleted")
            except Exception as e:
                st.error(f"Error loading users: {e}")

    # ---------------- STUDENT DASHBOARD ----------------
    if role == "student":
        st.header("Student Dashboard")
        try:
            courses = db.get_courses()
            enrolled = db.get_enrollments(user_id)

            # Available courses
            st.subheader("Available Courses")
            for c in courses:
                course_id = c["id"]
                title = c["title"]
                desc = c["description"]
                st.write(f"### {title}")
                st.write(desc)
                if course_id not in enrolled:
                    if st.button(f"Enroll {title}", key=f"enroll{course_id}"):
                        db.enroll(user_id, course_id)
                        st.success("Enrolled successfully")
                        st.experimental_rerun()

            # My courses
            st.subheader("My Courses")
            for c in courses:
                if c["id"] in enrolled:
                    course_id = c["id"]
                    st.write(f"## {c['title']}")
                    # Videos
                    st.write("### 🎥 Course Videos")
                    try:
                        videos = db.get_videos(course_id)
                        if not videos:
                            st.info("No videos available")
                        for v in videos:
                            v_title = v["title"]
                            v_url = v["path"]
                            st.write(f"#### {v_title}")
                            if "youtube.com/embed/" in v_url:
                                st.components.v1.iframe(v_url, height=400)
                            else:
                                st.video(v_url)
                    except Exception as e:
                        st.error(f"Error loading videos: {e}")

                    # Files
                    st.write("### 📁 Course Files")
                    try:
                        files = db.get_files(course_id)
                        if not files:
                            st.info("No files uploaded")
                        for f in files:
                            try:
                                with open(f["path"], "rb") as file_data:
                                    st.download_button(
                                        label=f"Download {f['title']}",
                                        data=file_data,
                                        file_name=f["title"]
                                    )
                            except FileNotFoundError:
                                st.warning(f"File not found: {f['title']}")
                    except Exception as e:
                        st.error(f"Error loading files: {e}")
        except Exception as e:
            st.error(f"Error loading student dashboard: {e}")
