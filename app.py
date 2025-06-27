import streamlit as st
import time
import os
from utils.auth import hash_password, check_password
from db import users_col, employees_col
from cloud import upload_image_to_cloudinary
from utils.face_utils import get_face_encodings
import numpy as np
from dotenv import load_dotenv
from db import attendance_col
import pandas as pd
load_dotenv()

st.set_page_config(page_title="FRA System")  # Set browser tab title

SESSION_EXPIRY_MINUTES = 30

# Styled page title
st.markdown("<h2 style='text-align: center;'>Face Recognition Attendance System</h2>", unsafe_allow_html=True)

# ---------- SESSION HELPERS ----------
def login_user(username, role, organization):
    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["role"] = role
    st.session_state["organization"] = organization
    st.session_state["login_time"] = time.time()

def logout_user():
    for key in ["logged_in", "username", "role", "organization", "login_time"]:
        st.session_state.pop(key, None)

def session_expired():
    if "login_time" in st.session_state:
        elapsed = (time.time() - st.session_state["login_time"]) / 60
        return elapsed > SESSION_EXPIRY_MINUTES
    return False

# ---------- MAIN ----------
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    if session_expired():
        st.warning("Session expired. Please log in again.")
        logout_user()
        st.stop()

    st.success(f"Logged in as {st.session_state['username']} ({st.session_state['role']})")
    if st.button("Logout"):
        logout_user()
        st.rerun()

    # ----------- DASHBOARD -----------
    

    if st.session_state["role"] == "admin":
        st.header("👤 Admin Dashboard")
        st.write(f"Manage your company's employees")

        # Upload new employee with labeled photo slots
        st.subheader("📤 Upload Employee Photos (Multiple Angles Recommended)")
        st.info("📌 Please upload clear face photos of the *same person* only. Use different angles like front, left, right, smile, etc.")

        if st.session_state.get("clear_emp_name", False):
            st.session_state["emp_name_input"] = ""
            st.session_state["emp_id_input"] = ""
            st.session_state["clear_emp_name"] = False

        emp_id = st.text_input("Employee ID", key="emp_id_input")
        emp_name = st.text_input("Employee Name", key="emp_name_input")

        # Predefined photo types
        photo_prompts = {
            "Front Face": None,
            "Slight Left Angle": None,
            "Slight Right Angle": None,
            "Smiling Expression": None,
            "Neutral with Good Lighting": None
        }

        # Create file uploaders for each prompt
        uploaded_images = {}
        for label in photo_prompts:
            uploaded_images[label] = st.file_uploader(f"📸 Upload: {label}", type=["jpg", "jpeg", "png"], key=f"{label}_upload")

        if "upload_success" in st.session_state:
            st.success(st.session_state["upload_success"])
            del st.session_state["upload_success"]

        if st.button("Save Images"):
            with st.spinner("Saving employee data..."):
                missing = []
                if not emp_id:
                    missing.append("employee ID")
                if not emp_name:
                    missing.append("employee name")

                valid_uploads = {k: v for k, v in uploaded_images.items() if v is not None}

                if not valid_uploads:
                    missing.append("at least one face image")

                if missing:
                    st.warning(f"Please provide {', '.join(missing)}.")
                else:
                    org = st.session_state["organization"]
                    username = st.session_state["username"]

                    exists = employees_col.find_one({
                        "employee_id": emp_id,
                        "organization": org
                    })

                    if exists:
                        st.error(f"❌ Employee ID '{emp_id}' already exists in your organization.")
                    else:
                        from utils.face_utils import get_face_encodings

                        encodings_list = []
                        urls_list = []
                        failed_images = []

                        for label, img in valid_uploads.items():
                            cloud_name = f"{emp_name.replace(' ', '_')}_{label.replace(' ', '_')}"
                            cloud_url = upload_image_to_cloudinary(img, cloud_name)

                            if cloud_url:
                                img.seek(0)
                                encs = get_face_encodings(img)
                                if encs:
                                    encodings_list.append(encs[0].tolist())
                                    urls_list.append(cloud_url)
                                else:
                                    failed_images.append(label)
                            else:
                                st.error(f"❌ Cloudinary upload failed for {label}")

                        if encodings_list:
                            employees_col.insert_one({
                                "employee_id": emp_id,
                                "employee_name": emp_name,
                                "organization": org,
                                "uploaded_by": username,
                                "image_urls": urls_list,
                                "face_encodings": encodings_list
                            })

                            st.session_state["upload_success"] = f"✅ Uploaded and saved {len(encodings_list)} valid photo(s) for '{emp_name}'."
                            st.session_state["clear_emp_name"] = True

                            if failed_images:
                                st.warning(f"⚠️ No face detected in: {', '.join(failed_images)}")

                            st.experimental_rerun()
                        else:
                            st.error("❌ No valid face found in any of the uploaded photos.")


        # Add space
        st.markdown("---\n\n\n")                    

        # Attendance Viewer
        st.subheader("📊 Attendance Viewer")

        org = st.session_state["organization"]
        records = list(attendance_col.find({"organization": org}))

        if records:
            df = pd.DataFrame(records)
            df = df.drop(columns=["_id", "organization"])

            # Filters
            employee_filter = st.selectbox("Filter by Employee", ["All"] + sorted(df["employee_name"].unique().tolist()))
            date_filter = st.date_input("Filter by Date", value=None)

            if employee_filter != "All":
                df = df[df["employee_name"] == employee_filter]
            if date_filter:
                df = df[df["date"] == date_filter.strftime("%Y-%m-%d")]

            st.dataframe(df)

            # CSV download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv, file_name="attendance.csv", mime="text/csv")
        else:
            st.info("No attendance records found yet.")

        st.write(f"Organization: `{st.session_state['organization']}`")


    elif st.session_state["role"] == "clerk":
        st.header("🕵️ Clerk Dashboard")
        st.write("Mark attendance using face recognition.")

        tab1, tab2 = st.tabs(["📤 Upload Group Photo", "📷 Real-time Webcam"])

        # --- Tab 1: Upload Group Photo ---
        with tab1:
            uploaded_img = st.file_uploader("Upload a group image", type=["jpg", "jpeg", "png"])
            
            if st.button("Mark Attendance from Image"):
                with st.spinner("Marking attendance..."):
                    if not uploaded_img:
                        st.warning("Please upload a photo with faces.")
                    else:
                        from utils.face_utils import recognize_faces_from_image

                        org = st.session_state["organization"]
                        recognized_names = recognize_faces_from_image(uploaded_img, org)

                        if recognized_names:
                            from datetime import datetime
                            import pytz
                            india = pytz.timezone("Asia/Kolkata")
                            now = datetime.now(india)

                            marked_names = []
                            skipped_names = []

                            for name in recognized_names:
                                employee = employees_col.find_one({"employee_name": name, "organization": org})
                                if employee:
                                    today = now.strftime("%Y-%m-%d")
                                    existing_logs = list(attendance_col.find({
                                        "employee_id": employee["employee_id"],
                                        "organization": org,
                                        "date": today
                                    }).sort("time", 1))

                                    if len(existing_logs) == 0:
                                        attendance_type = "IN"
                                    elif len(existing_logs) == 1:
                                        attendance_type = "OUT"
                                    else:
                                        attendance_type = None

                                    if attendance_type:
                                        attendance_col.insert_one({
                                            "employee_id": employee["employee_id"],
                                            "employee_name": name,
                                            "organization": org,
                                            "date": today,
                                            "time": now.strftime("%H:%M:%S"),
                                            "type": attendance_type
                                        })
                                        marked_names.append(name)
                                    else:
                                        skipped_names.append(name)

                            if marked_names:
                                st.success(f"✅ Marked attendance for: {', '.join(marked_names)}")
                            if skipped_names:
                                st.info(f"⚠️ IN and OUT entries already marked for: {', '.join(skipped_names)}")
                        else:
                            st.warning("😐 No known faces recognized.")

        # --- Tab 2: Webcam Mode (Per Person) ---
        with tab2:
            st.write("Open your webcam and click 'Capture & Match' to mark attendance.")

            captured_image = st.camera_input("Take photo")
            
            if st.button("Capture & Match"):
                with st.spinner("Marking attendance..."):
                    if not captured_image:
                        st.warning("Please capture a photo.")
                    else:
                        from utils.face_utils import recognize_faces_from_image

                        org = st.session_state["organization"]
                        recognized_names = recognize_faces_from_image(captured_image, org)

                        if recognized_names:
                            from datetime import datetime
                            import pytz
                            india = pytz.timezone("Asia/Kolkata")
                            now = datetime.now(india)

                            marked_names = []
                            skipped_names = []

                            for name in recognized_names:
                                employee = employees_col.find_one({"employee_name": name, "organization": org})
                                if employee:
                                    today = now.strftime("%Y-%m-%d")
                                    existing_logs = list(attendance_col.find({
                                        "employee_id": employee["employee_id"],
                                        "organization": org,
                                        "date": today
                                    }).sort("time", 1))

                                    if len(existing_logs) == 0:
                                        attendance_type = "IN"
                                    elif len(existing_logs) == 1:
                                        attendance_type = "OUT"
                                    else:
                                        attendance_type = None

                                    if attendance_type:
                                        attendance_col.insert_one({
                                            "employee_id": employee["employee_id"],
                                            "employee_name": name,
                                            "organization": org,
                                            "date": today,
                                            "time": now.strftime("%H:%M:%S"),
                                            "type": attendance_type
                                        })
                                        marked_names.append(name)
                                    else:
                                        skipped_names.append(name)

                            if marked_names:
                                st.success(f"✅ Marked attendance for: {', '.join(marked_names)}")
                            if skipped_names:
                                st.info(f"⚠️ IN and OUT entries already marked for: {', '.join(skipped_names)}")
                        else:
                            st.warning("😐 No known faces recognized.")

        # Add space
        st.markdown("---\n\n\n")
        
        st.subheader("📊 Attendance Viewer")

        org = st.session_state["organization"]
        records = list(attendance_col.find({"organization": org}))

        if records:
            df = pd.DataFrame(records)
            df = df.drop(columns=["_id", "organization"])

            # Filters
            employee_filter = st.selectbox("Filter by Employee", ["All"] + sorted(df["employee_name"].unique().tolist()))
            date_filter = st.date_input("Filter by Date", value=None)

            if employee_filter != "All":
                df = df[df["employee_name"] == employee_filter]
            if date_filter:
                df = df[df["date"] == date_filter.strftime("%Y-%m-%d")]

            st.dataframe(df)

            # CSV download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv, file_name="attendance.csv", mime="text/csv")
        else:
            st.info("No attendance records found yet.")
        
        st.write(f"Organization: `{st.session_state['organization']}`")


# ---------- DEFAULT / LOGIN / REGISTER ----------
else:
    st.info("👋 Welcome to the Face Recognition Attendance System. Please log in or register to get started.")
    choice = st.selectbox("Select Action", ["Login", "Register"])
        
    if choice == "Register":
        st.subheader("Create a New Account")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["admin", "clerk"])
        organization = st.text_input("Organization")

        if st.button("Register"):
            with st.spinner("Register process is going on..."):
                if username and password and organization:
                    if users_col.find_one({"username": username}):
                        st.error("Username already exists.")
                    else:
                        users_col.insert_one({
                            "username": username,
                            "password": hash_password(password),
                            "role": role,
                            "organization": organization
                        })
                        login_user(username, role, organization)
                        st.success("Registered and logged in successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill in all fields.")

    elif choice == "Login":
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            with st.spinner("Login process is going on..."):
                user = users_col.find_one({"username": username})
                if user and check_password(password, user["password"]):
                    login_user(user["username"], user["role"], user["organization"])
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
