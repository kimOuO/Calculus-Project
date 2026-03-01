#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Calculus OOM Backend - Docker Entrypoint${NC}"
echo -e "${BLUE}=========================================${NC}"

# Function to wait for database
wait_for_db() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo -e "${YELLOW}⏳ Waiting for ${service_name} to be ready...${NC}"
    
    # Use /dev/tcp for connection testing (more portable)
    while ! timeout 3 bash -c "exec 3<>/dev/tcp/$host/$port" 2>/dev/null; do
        echo -e "${YELLOW}   ${service_name} is unavailable - sleeping${NC}"
        sleep 2
    done
    
    echo -e "${GREEN}✅ ${service_name} is ready!${NC}"
}

# Wait for PostgreSQL
wait_for_db ${DB_HOST:-localhost} ${DB_PORT:-5432} "PostgreSQL"

# Wait for MongoDB
wait_for_db ${MONGO_HOST:-localhost} ${MONGO_PORT:-27017} "MongoDB"

echo -e "${BLUE}-----------------------------------------${NC}"
echo -e "${BLUE}Database Migration & Setup${NC}"
echo -e "${BLUE}-----------------------------------------${NC}"

# Create migrations if they don't exist
echo -e "${YELLOW}📝 Creating database migrations...${NC}"
python manage.py makemigrations --noinput

# Run migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${BLUE}-----------------------------------------${NC}"
echo -e "${BLUE}Database Connection Test${NC}"
echo -e "${BLUE}-----------------------------------------${NC}"

# Test database connections
python -c "
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.local')
django.setup()

from django.db import connection
from main.apps.Calculus_metadata.services.business import NoSqlDbBusinessService

# Test PostgreSQL connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    sys.exit(1)

# Test MongoDB connection
try:
    client = NoSqlDbBusinessService.get_connection()
    client.admin.command('ping')
    print('✅ MongoDB connection successful')
    client.close()
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    sys.exit(1)

print('🎉 All database connections are working!')
"

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}🚀 Starting Django Application...${NC}"
echo -e "${GREEN}=========================================${NC}"

# Fix permissions on Docker bind-mount directories so the app user can write
# (bind mounts are created as root by the Docker daemon on the host)
chown -R app:app /app/uploads /app/logs 2>/dev/null || true
chmod -R 755 /app/uploads /app/logs 2>/dev/null || true

# Drop to app user and execute the main command
exec gosu app "$@"