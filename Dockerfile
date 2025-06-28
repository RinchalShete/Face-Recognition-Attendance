# ✅ Use a prebuilt image with dlib + face_recognition already installed
FROM facegenius/face-recognition:latest

# Set working directory
WORKDIR /app

# Copy your project files into the container
COPY . .

# Install only your remaining Python packages (dlib/face_recognition already exist)
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port (you can still use 10000 if needed)
EXPOSE 8501

# Start the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

