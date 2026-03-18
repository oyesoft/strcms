import streamlit as st
import database as db

st.set_page_config(page_title="LMS", layout="wide")
st.title("📚 Simple LMS")

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.username = None

# ---------------- Login / Register ----------------
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
            st.experimental_rerun()
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
        st.experimental_rerun()

    if st.session_state.role == "student":
        st.subheader("Available Courses")
        courses = db.get_courses()
        for c in courses:
            st.write(f"**{c[1]}**")
            st.write(c[2])
            if st.button(f"Enroll in {c[1]}", key=f"enroll_{c[0]}"):
                db.enroll_course(st.session_state.user_id, c[0])
                st.success(f"Enrolled in {c[1]}!")

        st.subheader("My Courses")
        my_courses = db.get_enrolled_courses(st.session_state.user_id)
        for c in my_courses:
            st.write(f"**{c[1]}** - {c[2]}")

    elif st.session_state.role == "admin":
        st.subheader("Add Course")
        title = st.text_input("Course Title")
        desc = st.text_area("Course Description")
        if st.button("Add Course"):
            db.add_course(title, desc)
            st.success("Course added!")
