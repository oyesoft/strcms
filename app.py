import streamlit as st
import database as db

st.set_page_config(page_title="LMS with Videos", layout="wide")
st.title("📚 LMS with Video Lessons")

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.username = None

# ---------------- Login/Register ----------------
if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = db.login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.role = user[1]
            st.session_state.username = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid credentials")

    st.subheader("Register")
    new_username = st.text_input("New Username", key="reg_user")
    new_password = st.text_input("New Password", type="password", key="reg_pass")
    role = st.selectbox("Role", ["student", "admin"])
    if st.button("Register User"):
        try:
            db.add_user(new_username, new_password, role)
            st.success("User registered! Please login.")
        except:
            st.error("Username already exists.")

# ---------------- Dashboard ----------------
else:
    st.sidebar.write(f"Logged in as: {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False

    # ---------------- Student View ----------------
    if st.session_state.role == "student":
        st.subheader("My Courses")
        courses = db.get_enrolled_courses(st.session_state.user_id)
        if not courses:
            st.info("Enroll in a course from the Available Courses section below.")
        for c in courses:
            st.write(f"### {c[1]} - {c[2]}")
            lessons = db.get_lessons(c[0])
            for l in lessons:
                completed = db.get_lesson_progress(st.session_state.user_id, l[0])
                st.video(l[2]) if l[2] else st.write("No video URL provided")
                st.write(f"**{l[1]}** - {'✅ Completed' if completed else '❌ Not Completed'}")
                if not completed and st.button(f"Mark {l[1]} as Completed", key=f"complete_{l[0]}"):
                    db.mark_lesson_completed(st.session_state.user_id, l[0])
                    st.success(f"Lesson '{l[1]}' marked completed!")
                    completed = 1  # update local variable

        st.subheader("Available Courses to Enroll")
        all_courses = db.get_courses()
        for c in all_courses:
            if c not in courses:
                st.write(f"**{c[1]}** - {c[2]}")
                if st.button(f"Enroll in {c[1]}", key=f"enroll_{c[0]}"):
                    db.enroll_course(st.session_state.user_id, c[0])
                    st.success(f"Enrolled in {c[1]}!")

    # ---------------- Admin View ----------------
    elif st.session_state.role == "admin":
        st.subheader("Add Course")
        title = st.text_input("Course Title")
        desc = st.text_area("Course Description")
        if st.button("Add Course"):
            db.add_course(title, desc)
            st.success("Course added!")

        st.subheader("Add Lesson to Course")
        courses = db.get_courses()
        course_options = {c[1]: c[0] for c in courses}
        if courses:
            selected_course = st.selectbox("Select Course", options=list(course_options.keys()))
            lesson_title = st.text_input("Lesson Title", key="lesson_title")
            video_url = st.text_input("Video URL", key="lesson_video")
            if st.button("Add Lesson"):
                db.add_lesson(course_options[selected_course], lesson_title, video_url)
                st.success(f"Lesson added to {selected_course}!")
        else:
            st.info("Please add a course first.")
