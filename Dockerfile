FROM python:3.11-slim

LABEL maintainer="Heri Rusmanto <hvedaid@gmail.com>"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/var/www/mail-scheduler

# Set working directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    redis-tools \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser -d $APP_HOME -s /bin/bash appuser \
    && mkdir -p $APP_HOME \
    && chown -R appuser:appuser $APP_HOME

# Set up virtual environment
RUN python -m venv $VIRTUAL_ENV

# Install dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY --chown=appuser:appuser . .

# Set permissions
RUN chmod +x $APP_HOME/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command
CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "8080"]
