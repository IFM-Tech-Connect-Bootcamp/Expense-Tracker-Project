# Infrastructure Layer Deployment Guide

This guide provides step-by-step instructions for deploying the User Management infrastructure layer in different environments.

## Prerequisites

- Python 3.11+ with virtual environment
- PostgreSQL 14+ (production) or SQLite (development)
- Redis (optional, for caching)
- Docker (optional, for containerized deployment)

## Installation

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install infrastructure dependencies
pip install -r expense_tracker/server_app/user_management/infrastructure/requirements.txt
```

### 2. Database Setup

#### Development (SQLite)
```bash
# Run migrations to create tables
python manage.py migrate

# Verify database setup
python manage.py shell -c "
from user_management.infrastructure.orm.models import UserModel, OutboxEvent
print(f'Users table: {UserModel.objects.count()} rows')
print(f'Outbox table: {OutboxEvent.objects.count()} rows')
"
```

#### Production (PostgreSQL)
```bash
# Install PostgreSQL client
pip install psycopg2-binary

# Create database and user
createdb expense_tracker_db
createuser expense_tracker_user --pwprompt

# Configure Django settings
export DATABASE_URL="postgresql://expense_tracker_user:password@localhost/expense_tracker_db"

# Run migrations
python manage.py migrate
```

### 3. Environment Configuration

Create a `.env` file with the following settings:

```env
# Django Configuration
DJANGO_SECRET_KEY="your-secret-key-here"
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,your-domain.com"

# Database Configuration (Production)
DATABASE_URL="postgresql://user:password@localhost/expense_tracker_db"

# JWT Configuration
JWT_SECRET_KEY="your-jwt-secret-key-here"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Configuration
BCRYPT_ROUNDS=12
PASSWORD_REHASH_CHECK=True
PASSWORD_POLICY_TYPE="default"  # "default", "lenient", "strict"
PASSWORD_MIN_LENGTH=8

# Outbox Configuration
OUTBOX_AUTO_PROCESS=True
OUTBOX_BATCH_SIZE=100
OUTBOX_PROCESSING_INTERVAL_SECONDS=30
OUTBOX_MAX_RETRY_ATTEMPTS=3
OUTBOX_RETRY_DELAY_SECONDS=60
OUTBOX_WEBHOOK_TIMEOUT_SECONDS=30
OUTBOX_WEBHOOK_MAX_RETRIES=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 4. Django Settings Integration

Add to your Django `settings.py`:

```python
import os
from pathlib import Path

# Import infrastructure config
from user_management.infrastructure.config import InfrastructureConfig

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add user_management to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user_management',  # Add this
]

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'expense_tracker_db'),
        'USER': os.getenv('DB_USER', 'expense_tracker_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Infrastructure configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7'))

BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', '12'))
PASSWORD_REHASH_CHECK = os.getenv('PASSWORD_REHASH_CHECK', 'True').lower() == 'true'
PASSWORD_POLICY_TYPE = os.getenv('PASSWORD_POLICY_TYPE', 'default')
PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))

OUTBOX_AUTO_PROCESS = os.getenv('OUTBOX_AUTO_PROCESS', 'False').lower() == 'true'
OUTBOX_BATCH_SIZE = int(os.getenv('OUTBOX_BATCH_SIZE', '100'))
OUTBOX_PROCESSING_INTERVAL_SECONDS = int(os.getenv('OUTBOX_PROCESSING_INTERVAL_SECONDS', '30'))
OUTBOX_MAX_RETRY_ATTEMPTS = int(os.getenv('OUTBOX_MAX_RETRY_ATTEMPTS', '3'))

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': os.getenv('LOG_FORMAT', 
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'user_management.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'user_management': {
            'handlers': ['console', 'file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}
```

## Deployment Steps

### 1. Health Check

Run infrastructure health checks before deployment:

```bash
# Check all components
python manage.py check_infrastructure --component=all --verbose

# Check specific components
python manage.py check_infrastructure --component=database
python manage.py check_infrastructure --component=auth
python manage.py check_infrastructure --component=outbox
```

### 2. Database Migration

```bash
# Create and apply migrations
python manage.py makemigrations user_management
python manage.py migrate

# Verify migration success
python manage.py showmigrations user_management
```

### 3. Outbox Processing Setup

#### Option A: Background Processing (Recommended)
Set `OUTBOX_AUTO_PROCESS=True` in settings to enable automatic background processing.

#### Option B: Manual Processing
Run outbox processing manually or via cron:

```bash
# Process pending events once
python manage.py flush_outbox

# Process continuously in background
python manage.py flush_outbox --continuous

# Process with custom batch size
python manage.py flush_outbox --batch-size=50
```

#### Option C: Cron Job Setup
Add to crontab for regular processing:

```bash
# Process outbox every minute
* * * * * cd /path/to/project && python manage.py flush_outbox

# Process outbox every 5 minutes with logging
*/5 * * * * cd /path/to/project && python manage.py flush_outbox >> /var/log/outbox.log 2>&1
```

### 4. Service Monitoring

Set up monitoring for infrastructure services:

```bash
# Monitor outbox processing
tail -f user_management.log | grep outbox

# Monitor authentication events
tail -f user_management.log | grep auth

# Check for errors
tail -f user_management.log | grep ERROR
```

## Production Considerations

### Security

1. **Secret Key Management**
   - Use environment variables for all secrets
   - Rotate JWT secret keys periodically
   - Use strong bcrypt rounds (12+)

2. **Database Security**
   - Use dedicated database user with minimal permissions
   - Enable SSL connections
   - Regular security updates

3. **Password Policy**
   - Use `StrictPasswordPolicy` for high-security environments
   - Implement password expiration if required
   - Monitor failed authentication attempts

### Performance

1. **Database Optimization**
   - Create appropriate indexes (already included in migrations)
   - Use connection pooling
   - Monitor query performance

2. **Outbox Processing**
   - Adjust batch sizes based on load
   - Monitor processing times
   - Scale processing workers as needed

3. **Caching**
   - Cache frequently accessed user data
   - Use Redis for session storage
   - Implement query result caching

### Monitoring

1. **Health Checks**
   ```bash
   # Add to monitoring system
   python manage.py check_infrastructure --component=all
   ```

2. **Metrics Collection**
   - User registration rates
   - Authentication success/failure rates
   - Outbox processing metrics
   - Database performance metrics

3. **Alerting**
   - Failed outbox events
   - High authentication failure rates
   - Database connection issues
   - Service health check failures

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Run migrations and start server
CMD ["python", "manage.py", "migrate", "&&", "python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: expense_tracker_db
      POSTGRES_USER: expense_tracker_user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://expense_tracker_user:password@db/expense_tracker_db
      OUTBOX_AUTO_PROCESS: "true"
    depends_on:
      - db

  outbox_worker:
    build: .
    command: python manage.py flush_outbox --continuous
    environment:
      DATABASE_URL: postgresql://expense_tracker_user:password@db/expense_tracker_db
    depends_on:
      - db

volumes:
  postgres_data:
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Verify Python path
   python -c "import user_management.infrastructure; print('OK')"
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   python manage.py dbshell
   ```

3. **Migration Issues**
   ```bash
   # Reset migrations (development only)
   python manage.py migrate user_management zero
   python manage.py migrate user_management
   ```

4. **Outbox Processing Issues**
   ```bash
   # Check outbox events
   python manage.py shell -c "
   from user_management.infrastructure.orm.models import OutboxEvent
   print(OutboxEvent.objects.filter(status='failed').count())
   "
   ```

### Log Analysis

```bash
# Check for authentication issues
grep "authentication" user_management.log

# Check for outbox processing issues
grep "outbox" user_management.log | grep ERROR

# Monitor performance
grep "processing_time" user_management.log
```

## Maintenance

### Regular Tasks

1. **Database Maintenance**
   ```bash
   # Clean up old outbox events (older than 30 days)
   python manage.py shell -c "
   from datetime import datetime, timedelta
   from user_management.infrastructure.orm.models import OutboxEvent
   cutoff = datetime.now() - timedelta(days=30)
   OutboxEvent.objects.filter(created_at__lt=cutoff, status='delivered').delete()
   "
   ```

2. **Log Rotation**
   ```bash
   # Rotate logs weekly
   logrotate -f /etc/logrotate.d/user_management
   ```

3. **Security Updates**
   ```bash
   # Update dependencies
   pip install -r requirements.txt --upgrade
   
   # Check for security vulnerabilities
   pip audit
   ```

This deployment guide ensures a robust, secure, and maintainable infrastructure layer deployment.