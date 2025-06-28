FROM python:3.10-slim

# Install system dependencies (including SSL stuff)
RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libboost-all-dev \
    libssl-dev libffi-dev \
    libpython3-dev python3-dev \
    libopencv-dev \
    curl \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port for Streamlit
EXPOSE 8501

# Run your app
CMD ["streamlit", "run", "app.py"]
