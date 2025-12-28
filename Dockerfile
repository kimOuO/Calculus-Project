FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt /app/requirements/base.txt
RUN pip install --upgrade pip && \
    pip install -r requirements/base.txt

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Run migrations
RUN python manage.py makemigrations || true

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
