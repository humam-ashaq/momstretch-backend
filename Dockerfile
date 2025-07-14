# Gunakan base image Python 3.12 slim
FROM python:3.12-slim

# Install dependencies OS level (libGL untuk OpenCV)
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Buat working directory
WORKDIR /app

# Salin semua file ke container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (optional, untuk lokal)
EXPOSE 8080

# Jalankan Gunicorn (pastikan "app" = nama file dan "app" = nama variabel Flask)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
