FROM python:3.10-slim

# Install system dependencies for dlib, face_recognition, and image handling
RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libboost-all-dev \
    libssl-dev libffi-dev \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    libpython3-dev python3-dev \
    libopencv-dev \
    curl ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by Streamlit
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

