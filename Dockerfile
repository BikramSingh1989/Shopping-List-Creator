FROM python:3.11

WORKDIR /app

# Install system dependencies (needed for pymongo + SSL)
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run app with Gunicorn in production
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:10000", "app:app"]
