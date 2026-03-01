FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=main.settings.local
ENV MPLCONFIGDIR=/tmp/matplotlib

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    netcat-openbsd \
    fonts-wqy-zenhei \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN addgroup --system app && adduser --system --group app

# Install Python dependencies
COPY requirements/base.txt /app/requirements/base.txt
COPY requirements/local.txt /app/requirements/local.txt
RUN pip install --upgrade pip && \
    pip install -r requirements/local.txt

# Copy project files
COPY --chown=app:app . /app/

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/uploads /app/staticfiles /app/media && \
    chown -R app:app /app && \
    chmod -R 755 /app

# Copy entrypoint script (run as root so entrypoint can fix bind-mount permissions)
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
