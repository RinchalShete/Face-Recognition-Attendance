# 📸 Face Recognition Attendance System

A modern, web-based attendance system that uses **face recognition** to mark attendance with ease and accuracy. Built with **Streamlit**, **MongoDB**, **Cloudinary**, and `face_recognition`, it supports **role-based access**, **multi-photo employee registration**, **IN/OUT logic**, and **real-time recognition**.

---

## 🚀 Features

### 🧑‍💼 Role-Based Login
- **Admin**:  
  - Register employees with multiple face photos (front, left, right, etc.)
  - View attendance records  
- **Clerk**:  
  - Mark attendance using webcam or group image
  - View attendance records

---

### 📤 Multi-Photo Employee Registration
- Admins upload **multiple labeled face images per employee**
- Each image is uploaded to **Cloudinary**
- Face encodings from these images are stored in **MongoDB**

---

### 🤖 Face Recognition Attendance
- Attendance can be marked using:
  - 📷 **Webcam**
  - 🖼️ **Group Photo Upload**
- Each face is matched against known encodings
- **IN/OUT attendance logic**:
  - First entry → IN
  - Second entry → OUT
  - Already 2 entries → Message shown and skipped
  

---

### 🗂️ Attendance Viewer
- Shown in both Admin and Clerk dashboards
- Displays:
  - Employee ID
  - Name
  - Date
  - Time
- Filters:
  - By Employee
  - By Date
- Exports attendance as **CSV**
- Only shows employees of the **current organization**

---

### 🌍 Timezone-Aware Logs
- Uses local Indian time `Asia/Kolkata`
- Attendance stored with separate `date` and `time` fields (no combined timestamp)

---

### ☁️ Cloud Storage & Database
- Employee images stored on **Cloudinary**
- All data stored in **MongoDB**, including:
  - Users
  - Employees (with multiple encodings)
  - Attendance (with IN/OUT entries)

---

### 🐳 Dockerized
- Fully containerized using **Docker**
- Easily run anywhere with a single command

---

## 🛠️ Tech Stack

| Tool             | Usage                            |
|------------------|----------------------------------|
| Python           | Core logic and backend           |
| Streamlit        | Web interface                    |
| face_recognition | Face encoding and comparison     |
| MongoDB          | User, employee, and attendance DB|
| Cloudinary       | Cloud image hosting              |
| Docker           | Containerization & portability   |
| dotenv           | Manage environment variables     |

---

## 📦 Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/RinchalShete/Face-Recognition-Attendance.git
cd Face-Recognition-Attendance
```

### 2. Set up Environment Variables
Create a .env file in the root folder:
```bash
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGO_DB=face_attendance

CLOUD_NAME=your_cloud_name
CLOUD_API_KEY=your_api_key
CLOUD_API_SECRET=your_api_secret
```
### 3. Build Docker Image
```bash
docker build -t fra-app .
```
### 4. Run the App 
```bash
docker run --env-file .env -p 8501:8501 -v "$PWD":/app fra-app
```
Open in browser: http://localhost:8501
