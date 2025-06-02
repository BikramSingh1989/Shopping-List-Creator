# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for SSL + pymongo
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (Render will set $PORT)
EXPOSE 10000

# Run app with dynamic port from $PORT
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:${PORT}", "app:app"]
