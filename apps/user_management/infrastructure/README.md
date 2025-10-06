# User Management Infrastructure Layer

This layer provides concrete implementations of domain service interfaces using Django ORM, external libraries, and infrastructure concerns following clean architecture principles.

## Architecture Overview

The infrastructure layer implements:

- **ORM Models**: Django models for database persistence
- **Repository Pattern**: Concrete repository implementations using Django ORM
- **Authentication Services**: Password hashing and JWT token management
- **Transactional Outbox Pattern**: Reliable event delivery to external systems
- **Event Subscribers**: Domain event handlers for external integrations
- **Dependency Injection**: Service container for managing dependencies

## Components

### ORM (`orm/`)

- `models.py`: Django models for User and OutboxEvent entities
- `mappers.py`: Bidirectional mapping between domain entities and ORM models

### Repositories (`repositories/`)

- `user_repository.py`: Django ORM implementation of UserRepository interface

### Authentication (`auth/`)

- `password_hasher.py`: Bcrypt-based password hashing service
- `token_provider.py`: JWT token generation and validation service

### Outbox Pattern (`outbox/`)

- `writer.py`: Transactional event writing to outbox table
- `dispatcher.py`: Background processing and delivery of outbox events

### Event Handling (`subscribers/`)

- `notify_on_user_events.py`: Domain event subscribers for external notifications

### Configuration

- `config.py`: Infrastructure configuration management
- `container.py`: Dependency injection container
- `apps.py`: Django app configuration and event bus setup

## Key Features

### Transactional Outbox Pattern

Ensures reliable event delivery to external systems:

```python
# Events are written to database in same transaction as domain changes
await write_domain_event(user_registered_event)

# Background processor delivers events reliably
python manage.py flush_outbox --continuous
```

### Async/Await Support

Full async implementation throughout:

```python
user = await repository.find_by_id(user_id)
await repository.save(user)
```

### Error Translation

Domain-specific errors from infrastructure exceptions:

```python
try:
    # Django ORM operation
except IntegrityError as e:
    if "email" in str(e):
        raise DuplicateEmailError(email)
    raise
```

### Type Safety

Strict typing throughout with Protocol-based interfaces:

```python
class PasswordHasher(Protocol):
    async def hash_password(self, password: str) -> str: ...
    async def verify_password(self, password: str, hash: str) -> bool: ...
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
```

### Outbox Events Table

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP NULL,
    error_message TEXT NULL
);
```

## Configuration

### Django Settings

```python
# JWT Configuration
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Hashing
BCRYPT_ROUNDS = 12
PASSWORD_REHASH_CHECK = True

# Outbox Processing
OUTBOX_AUTO_PROCESS = True
OUTBOX_BATCH_SIZE = 100
OUTBOX_PROCESSING_INTERVAL_SECONDS = 30
OUTBOX_MAX_RETRY_ATTEMPTS = 3
```

### App Registration

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'user_management',
]

# Configure app
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

## Usage Examples

### Repository Usage

```python
from user_management.infrastructure import DjangoUserRepository

repository = DjangoUserRepository()

# Find user by email
user = await repository.find_by_email("user@example.com")

# Save user changes
await repository.save(user)
```

### Authentication Services

```python
from user_management.infrastructure import BcryptPasswordHasher, JWTTokenProvider

# Hash password
hasher = BcryptPasswordHasher()
hash = await hasher.hash_password("password123")

# Generate JWT token
token_provider = JWTTokenProvider()
token = await token_provider.generate_access_token(user_id, claims)
```

### Event Outbox

```python
from user_management.infrastructure.outbox import write_domain_event

# Write event reliably
await write_domain_event(user_registered_event)

# Process outbox events
python manage.py flush_outbox
```

## Dependencies

Core dependencies:

- Django 4.2+ (ORM and web framework)
- passlib[bcrypt] (password hashing)
- PyJWT (JWT tokens)
- psycopg2-binary (PostgreSQL adapter)

Development dependencies:

- pytest + pytest-django (testing)
- mypy (type checking)
- black + isort (code formatting)

## Testing

Infrastructure components include comprehensive test coverage:

```bash
# Run infrastructure tests
pytest user_management/infrastructure/tests/

# Run with coverage
pytest --cov=user_management.infrastructure
```

## Performance Considerations

- Database indexes on frequently queried columns
- Connection pooling for database access
- Async operations to avoid blocking
- Batch processing for outbox events
- Configurable retry mechanisms

## Security Features

- Bcrypt password hashing with configurable rounds
- JWT tokens with expiration and refresh
- SQL injection protection via ORM
- Input validation and sanitization
- Secure random token generation

## Monitoring and Observability

- Comprehensive logging throughout
- Structured error handling
- Performance metrics via Django middleware
- Health checks for external dependencies
- Audit trails via outbox events

## Production Deployment

1. Run database migrations:
   ```bash
   python manage.py migrate
   ```

2. Start outbox processor:
   ```bash
   python manage.py flush_outbox --continuous
   ```

3. Configure environment variables for production settings

4. Set up monitoring and alerting for outbox processing

5. Configure backup and recovery procedures for database