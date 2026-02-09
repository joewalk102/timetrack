FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GCP_PROJECT_ID="" \
    GCP_SECRET_NAME="" \
    CERT_URL=""

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy the application code
COPY . .
RUN python manage.py collectstatic --noinput

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose the port Cloud Run will use
EXPOSE ${PORT}

# Run the application with Gunicorn
CMD curl --create-dirs -o $HOME/.postgresql/root.crt ${CERT_URL} && \
    chmod 600 $HOME/.postgresql/root.crt && \
    exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    TimeTrack.wsgi:application
