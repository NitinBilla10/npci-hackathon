# ./model_retraining/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .
COPY crontab /etc/cron.d/model-retrain-crontab

# Give execution permissions to the cron job
RUN chmod 0644 /etc/cron.d/model-retrain-crontab

# Apply cron job
RUN crontab /etc/cron.d/model-retrain-crontab

# Make sure model directory exists
RUN mkdir -p /app/model/backups

# Run cron in foreground
CMD ["cron", "-f"]