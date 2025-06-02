FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for SSL, MongoDB, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Use gunicorn in production
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:10000", "app:app"]
