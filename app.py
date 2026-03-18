import streamlit as st
import database as db
import re

st.set_page_config(page_title="Free LMS with Videos", layout="wide")
st.title("📚 LMS with Video Lessons (Free Hosting)")

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

    # ---------------- Helper Function ----------------
    def play_video(url):
        if not url:
            st.info("No video URL provided for this lesson.")
            return

        # Regular YouTube video
        youtube_match = re.match(r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+', url)
        # Raw MP4
        mp4_match = url.endswith(".mp4")
        # YouTube live
        live_match = re.match(r'(https?://)?(www\.)?youtube\.com/live/[\w-]+', url)

        if youtube_match or mp4_match:
            st.video(url)
        elif live_match:
            video_id = url.split("/")[-1]
            st.markdown(f"""
            <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" 
            frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"Cannot play video: '{url}'. Use YouTube watch?v=... or raw .mp4 link.")

    # ---------------- Student Dashboard ----------------
    if st.session_state.role == "student":
        st.subheader("My Courses")
        enrolled_courses = db.get_enrolled_courses(st.session_state.user_id)
        if not enrolled_courses:
            st.info("Enroll in a course from the Available Courses section below.")

        for course in enrolled_courses:
            st.write(f"### {course[1]} - {course[2]}")
            lessons = db.get_lessons(course[0])
            for lesson in lessons:
                completed = db.get_lesson_progress(st.session_state.user_id, lesson[0])
                play_video(lesson[2])
                st.write(f"**{lesson[1]}** - {'✅ Completed' if completed else '❌ Not Completed'}")
                if not completed and st.button(f"Mark {lesson[1]} as Completed", key=f"complete_{lesson[0]}"):
                    db.mark_lesson_completed(st.session_state.user_id, lesson[0])
                    st.success(f"Lesson '{lesson[1]}' marked completed!")
                    completed = 1

        st.subheader("Available Courses to Enroll")
        all_courses = db.get_courses()
        for course in all_courses:
            if course not in enrolled_courses:
                st.write(f"**{course[1]}** - {course[2]}")
                if st.button(f"Enroll in {course[1]}", key=f"enroll_{course[0]}"):
                    db.enroll_course(st.session_state.user_id, course[0])
                    st.success(f"Enrolled in {course[1]}!")

    # ---------------- Admin Dashboard ----------------
    elif st.session_state.role == "admin":
        st.subheader("Add Course")
        course_title = st.text_input("Course Title")
        course_desc = st.text_area("Course Description")
        if st.button("Add Course"):
            db.add_course(course_title, course_desc)
            st.success("Course added!")

        st.subheader("Manage Lessons")
        courses = db.get_courses()
        if courses:
            course_options = {c[1]: c[0] for c in courses}
            selected_course = st.selectbox("Select Course", options=list(course_options.keys()))

            # Add new lesson
            st.markdown("**Add New Lesson**")
            lesson_title = st.text_input("Lesson Title", key="lesson_title")
            video_url = st.text_input("Video URL (YouTube/MP4/Live link)", key="lesson_video")
            if st.button("Add Lesson"):
                db.add_lesson(course_options[selected_course], lesson_title, video_url)
                st.success(f"Lesson '{lesson_title}' added to {selected_course}!")

            # List existing lessons with delete buttons
            st.markdown("**Existing Lessons**")
            lessons = db.get_lessons(course_options[selected_course])
            if lessons:
                for l in lessons:
                    st.write(f"**{l[1]}** - {l[2] if l[2] else 'No video URL'}")
                    if st.button(f"Delete {l[1]}", key=f"delete_{l[0]}"):
                        db.delete_lesson(l[0])
                        st.success(f"Lesson '{l[1]}' deleted!")
            else:
                st.info("No lessons for this course yet.")
        else:
            st.info("Please add a course first.")
