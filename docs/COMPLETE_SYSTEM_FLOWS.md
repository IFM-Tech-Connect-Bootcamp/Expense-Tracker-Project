# Complete System Flows - User Management Bounded Context

## Overview

This document provides a comprehensive trace of every use case through the entire system architecture, from HTTP request entry point to final HTTP response. Each flow shows the exact path through all layers: Presentation → Application → Domain → Infrastructure and back.

## 🏗️ System Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    📡 HTTP REQUEST                              │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                🎯 PRESENTATION LAYER                            │
│  • Views (API endpoints)                                        │
│  • Serializers (Request/Response validation)                    │
│  • Authentication (JWT middleware)                              │
│  • Error handling & HTTP status codes                           │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                📋 APPLICATION LAYER                             │
│  • Commands (Use case inputs)                                   │
│  • Handlers (Use case orchestration)                            │
│  • DTOs (Data transfer objects)                                 │
│  • Event publishing                                             │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                🏛️ DOMAIN LAYER                                  │
│  • Entities (Business logic)                                    │
│  • Value Objects (Domain primitives)                            │
│  • Domain Events (State changes)                                │
│  • Business Rules (Domain invariants)                           │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                🔧 INFRASTRUCTURE LAYER                          │
│  • Repository Implementation (Data persistence)                 │
│  • Authentication Services (Password & JWT)                     │
│  • Outbox Writer (Event persistence)                            │
│  • Database Integration (Django ORM)                            │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    💾 DATABASE                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Use Case Flow #1: User Registration

### 📡 **HTTP Request Entry**
```http
POST /api/v1/users/auth/register/
Content-Type: application/json
Authorization: Not required

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

### 🎯 **Presentation Layer Flow**

#### Step 1: URL Routing
```python
# File: apps/user_management/presentation/urls.py
path('auth/register/', register_user, name='register_user')
```

#### Step 2: View Function Entry
```python
# File: apps/user_management/presentation/views.py
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register_user(request: Request) -> Response:
```

#### Step 3: Request Validation
```python
# File: apps/user_management/presentation/serializers.py
serializer = RegisterUserSerializer(data=request.data)
if not serializer.is_valid():
    return Response({"error": "Validation failed"}, status=400)

# RegisterUserSerializer validation:
# - Email format validation
# - Password minimum length (8 chars)
# - First/last name normalization (title case)
# - Required field validation
```

#### Step 4: Command Creation
```python
# File: apps/user_management/presentation/views.py
register_command = RegisterUserCommand(
    email=serializer.validated_data['email'],
    password=serializer.validated_data['password'],
    first_name=serializer.validated_data['first_name'],
    last_name=serializer.validated_data['last_name'],
)
```

### 📋 **Application Layer Flow**

#### Step 5: Infrastructure Container Resolution
```python
# File: apps/user_management/presentation/views.py
container = InfrastructureContainer()
handler = RegisterUserHandler(
    user_repository=container.get(UserRepository),
    password_service=container.get(PasswordHasher),
)
```

#### Step 6: Handler Execution
```python
# File: apps/user_management/application/handlers/register_user.py
def handle(self, command: RegisterUserCommand) -> RegisterUserResult:
```

#### Step 7: Command Validation
```python
# File: apps/user_management/application/handlers/register_user.py
# Create domain value objects
email = Email(command.email)           # Email validation & normalization
first_name = FirstName(command.first_name)  # Name validation & normalization
last_name = LastName(command.last_name)     # Name validation & normalization
```

#### Step 8: Business Rule Check - User Existence
```python
# File: apps/user_management/application/handlers/register_user.py
existing_user = self._user_repository.find_by_email(email)
if existing_user is not None:
    raise UserAlreadyExistsError(email.value)
```

### 🏛️ **Domain Layer Flow**

#### Step 9: Password Hashing (Infrastructure Service)
```python
# File: apps/user_management/application/handlers/register_user.py
password_hash = self._password_service.hash_password(command.password)
# → Calls infrastructure bcrypt hasher
# → Returns PasswordHash value object
```

#### Step 10: User Entity Creation
```python
# File: apps/user_management/domain/entities/user.py
user = User.create(
    email=email,
    password_hash=PasswordHash(password_hash),
    first_name=first_name,
    last_name=last_name
)

# Inside User.create():
# 1. Generate new UserId
# 2. Set timestamps
# 3. Set status to ACTIVE
# 4. Publish UserRegistered domain event
# 5. Return User entity
```

#### Step 11: Domain Event Generation
```python
# File: apps/user_management/domain/entities/user.py
# Automatically generated in User.create()
user_registered_event = UserRegistered(
    event_id=str(uuid.uuid4()),
    occurred_at=datetime.utcnow(),
    user_data={
        "id": str(self.id.value),
        "email": self.email.value,
        "first_name": self.first_name.value,
        "last_name": self.last_name.value,
        "status": self.status.value
    }
)
```

### 🔧 **Infrastructure Layer Flow**

#### Step 12: User Persistence
```python
# File: apps/user_management/infrastructure/repositories/user_repository_django.py
def save(self, user: User) -> User:
    # 1. Convert domain entity to ORM model
    # 2. Save to database
    # 3. Convert back to domain entity
    # 4. Return persisted user
```

#### Step 13: Event Persistence (Outbox Pattern)
```python
# File: apps/user_management/infrastructure/outbox/writer.py
# Events collected from user.get_domain_events()
for event in user_result.events:
    write_domain_event(event, use_transaction_commit=False)
    # → Stores event in outbox table for reliable delivery
```

### 📋 **Application Layer Response**

#### Step 14: DTO Creation
```python
# File: apps/user_management/application/handlers/register_user.py
user_dto = UserDTO(
    id=str(user.id.value),
    email=user.email.value,
    first_name=user.first_name.value,
    last_name=user.last_name.value,
    status=user.status.value,
    created_at=user.created_at,
    updated_at=user.updated_at
)
```

### 🎯 **Presentation Layer Response**

#### Step 15: Response Serialization
```python
# File: apps/user_management/presentation/views.py
user_data = _create_user_response_data(user_dto)
return Response(user_data, status=status.HTTP_201_CREATED)
```

### 📡 **HTTP Response**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "0195f7d6-41ec-441c-a615-00a709f26e93",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "status": "active",
  "created_at": "2025-10-06T12:00:00.000Z",
  "updated_at": "2025-10-06T12:00:00.000Z"
}
```

---

## 🔄 Use Case Flow #2: User Authentication

### 📡 **HTTP Request Entry**
```http
POST /api/v1/users/auth/login/
Content-Type: application/json
Authorization: Not required

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### 🎯 **Presentation Layer Flow**

#### Step 1: URL Routing
```python
# File: apps/user_management/presentation/urls.py
path('auth/login/', authenticate_user, name='authenticate_user')
```

#### Step 2: View Function Entry
```python
# File: apps/user_management/presentation/views.py
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def authenticate_user(request: Request) -> Response:
```

#### Step 3: Request Validation
```python
# File: apps/user_management/presentation/serializers.py
serializer = AuthenticateUserSerializer(data=request.data)
# Validates email format and password presence
```

#### Step 4: Command Creation
```python
auth_command = AuthenticateUserCommand(
    email=serializer.validated_data['email'],
    password=serializer.validated_data['password'],
)
```

### 📋 **Application Layer Flow**

#### Step 5: Handler Execution
```python
# File: apps/user_management/application/handlers/authenticate_user.py
def handle(self, command: AuthenticateUserCommand) -> AuthResultDTO:
```

#### Step 6: User Lookup
```python
# File: apps/user_management/application/handlers/authenticate_user.py
email = Email(command.email)
user = self._user_repository.find_by_email(email)
if user is None:
    raise InvalidCredentialsError(email.value)
```

### 🏛️ **Domain Layer Flow**

#### Step 7: Password Verification
```python
# File: apps/user_management/domain/entities/user.py
is_valid = user.verify_password(
    command.password,
    self._password_service
)
# → Calls infrastructure password verification
# → Returns boolean result
```

#### Step 8: User Status Check
```python
# File: apps/user_management/domain/entities/user.py
if not user.is_active():
    raise UserDeactivatedError(str(user.id.value))
```

### 🔧 **Infrastructure Layer Flow**

#### Step 9: JWT Token Generation
```python
# File: apps/user_management/infrastructure/auth/jwt_provider.py
access_token = self._token_provider.issue_token(user.id)
# → Creates JWT with user ID as subject
# → Signs with secret key
# → Sets expiration time
```

### 📋 **Application Layer Response**

#### Step 10: Authentication Result Creation
```python
# File: apps/user_management/application/handlers/authenticate_user.py
auth_result = AuthResultDTO(
    user=user_dto,
    access_token=access_token,
    token_type="Bearer",
    expires_in=settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME']
)
```

### 🎯 **Presentation Layer Response**

#### Step 11: Response Formatting
```python
# File: apps/user_management/presentation/views.py
response_data = {
    "user": user_data,
    "access_token": auth_result.access_token,
    "token_type": "Bearer",
    "expires_in": settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME'],
}
return Response(response_data, status=status.HTTP_200_OK)
```

### 📡 **HTTP Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "user": {
    "id": "0195f7d6-41ec-441c-a615-00a709f26e93",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "status": "active",
    "created_at": "2025-10-06T12:00:00.000Z",
    "updated_at": "2025-10-06T12:00:00.000Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

## 🔄 Use Case Flow #3: Get Current User Profile

### 📡 **HTTP Request Entry**
```http
GET /api/v1/users/profile/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 🎯 **Presentation Layer Flow**

#### Step 1: Authentication Middleware
```python
# File: apps/user_management/presentation/authentication.py
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        # 1. Extract Bearer token from Authorization header
        # 2. Verify token signature and expiration
        # 3. Extract user ID from token claims
        # 4. Lookup user in repository
        # 5. Return UserProxy for Django compatibility
```

#### Step 2: Token Extraction
```python
# File: apps/user_management/presentation/authentication.py
header = self.get_authorization_header(request)
token = self.get_token_from_header(header)
```

#### Step 3: Token Verification
```python
# File: apps/user_management/infrastructure/auth/jwt_provider.py
user_id = self.token_provider.verify_token(token)
# → Verifies JWT signature
# → Checks expiration
# → Returns UserId
```

#### Step 4: User Lookup for Authentication
```python
# File: apps/user_management/presentation/authentication.py
user = self.user_repository.find_by_id(user_id)
if not user or not user.is_active():
    raise AuthenticationFailed("User account is not active")
```

#### Step 5: View Function Entry
```python
# File: apps/user_management/presentation/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request: Request) -> Response:
```

#### Step 6: Current User Extraction
```python
# File: apps/user_management/presentation/views.py
current_user = get_current_user_from_request(request)
# → Extracts authenticated user from request.user
```

### 📋 **Application Layer Flow**

#### Step 7: DTO Conversion
```python
# File: apps/user_management/presentation/views.py
user_data = _create_user_response_data(UserDTO(
    id=str(current_user.id.value),
    email=current_user.email.value,
    first_name=current_user.first_name.value,
    last_name=current_user.last_name.value,
    full_name=f"{current_user.first_name.value} {current_user.last_name.value}",
    status=current_user.status.value,
    created_at=current_user.created_at,
    updated_at=current_user.updated_at
))
```

### 🎯 **Presentation Layer Response**

#### Step 8: Response Return
```python
return Response(user_data, status=status.HTTP_200_OK)
```

### 📡 **HTTP Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "0195f7d6-41ec-441c-a615-00a709f26e93",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "status": "active",
  "created_at": "2025-10-06T12:00:00.000Z",
  "updated_at": "2025-10-06T12:00:00.000Z"
}
```

---

## 🔄 Use Case Flow #4: Update User Profile

### 📡 **HTTP Request Entry**
```http
PUT /api/v1/users/profile/update/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com"
}
```

### 🎯 **Presentation Layer Flow**

#### Step 1-5: Authentication Flow
*Same as Get Current User Profile (Steps 1-5)*

#### Step 6: Request Validation
```python
# File: apps/user_management/presentation/serializers.py
serializer = UpdateProfileSerializer(data=request.data)
# Validates optional fields, at least one required
# Normalizes email and names
```

#### Step 7: Command Creation
```python
update_command = UpdateProfileCommand(
    user_id=str(current_user.id.value),
    new_email=serializer.validated_data.get('email'),
    new_first_name=serializer.validated_data.get('first_name'),
    new_last_name=serializer.validated_data.get('last_name'),
)
```

### 📋 **Application Layer Flow**

#### Step 8: Handler Execution
```python
# File: apps/user_management/application/handlers/update_profile.py
def handle(self, command: UpdateProfileCommand) -> UpdateProfileResult:
```

#### Step 9: User Lookup
```python
user_id = UserId.from_string(command.user_id)
user = self._user_repository.find_by_id(user_id)
```

#### Step 10: Profile Value Preparation
```python
# File: apps/user_management/application/handlers/update_profile.py
new_email = Email(command.new_email) if command.new_email else None
new_first_name = FirstName(command.new_first_name) if command.new_first_name else None
new_last_name = LastName(command.new_last_name) if command.new_last_name else None
```

### 🏛️ **Domain Layer Flow**

#### Step 11: Profile Update (Domain Method)
```python
# File: apps/user_management/domain/entities/user.py
user.update_profile(
    new_email=new_email,
    new_first_name=new_first_name,
    new_last_name=new_last_name
)

# Inside User.update_profile():
# 1. Validate changes (at least one field changed)
# 2. Update fields that are provided
# 3. Update timestamp
# 4. Generate UserProfileUpdated domain event
# 5. Record changes for audit
```

#### Step 12: Domain Event Generation
```python
# File: apps/user_management/domain/entities/user.py
profile_updated_event = UserProfileUpdated(
    event_id=str(uuid.uuid4()),
    occurred_at=datetime.utcnow(),
    user_data={...},
    changes={
        "email": {"old": old_email, "new": new_email},
        "first_name": {"old": old_first_name, "new": new_first_name},
        "last_name": {"old": old_last_name, "new": new_last_name}
    }
)
```

### 🔧 **Infrastructure Layer Flow**

#### Step 13: User Persistence
```python
# File: apps/user_management/infrastructure/repositories/user_repository_django.py
updated_user = self._user_repository.update(user)
```

#### Step 14: Event Persistence
```python
# File: apps/user_management/infrastructure/outbox/writer.py
# Events collected and persisted to outbox
for event in update_result.events:
    write_domain_event(event)
```

### 📋 **Application Layer Response**

#### Step 15: DTO Creation
```python
user_dto = UserDTO(
    # ... updated user data
)
```

### 🎯 **Presentation Layer Response**

#### Step 16: Response Return
```python
user_data = _create_user_response_data(update_result.user_dto)
return Response(user_data, status=status.HTTP_200_OK)
```

### 📡 **HTTP Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "0195f7d6-41ec-441c-a615-00a709f26e93",
  "email": "jane.smith@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "status": "active",
  "created_at": "2025-10-06T12:00:00.000Z",
  "updated_at": "2025-10-06T12:05:00.000Z"
}
```

---

## 🔄 Use Case Flow #5: Change Password

### 📡 **HTTP Request Entry**
```http
POST /api/v1/users/profile/change-password/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "old_password": "SecurePassword123!",
  "new_password": "NewSecurePassword456!"
}
```

### 🎯 **Presentation Layer Flow**

#### Step 1-5: Authentication Flow
*Same as Get Current User Profile (Steps 1-5)*

#### Step 6: Request Validation
```python
# File: apps/user_management/presentation/serializers.py
serializer = ChangePasswordSerializer(data=request.data)
# Validates both passwords are provided
# Ensures minimum password length
# Passwords are write-only fields
```

#### Step 7: Command Creation
```python
change_password_command = ChangePasswordCommand(
    user_id=str(current_user.id.value),
    old_password=serializer.validated_data['old_password'],
    new_password=serializer.validated_data['new_password'],
)
```

### 📋 **Application Layer Flow**

#### Step 8: Handler Execution
```python
# File: apps/user_management/application/handlers/change_password.py
def handle(self, command: ChangePasswordCommand) -> ChangePasswordResult:
```

#### Step 9: User Lookup
```python
user_id = UserId.from_string(command.user_id)
user = self._user_repository.find_by_id(user_id)
```

### 🏛️ **Domain Layer Flow**

#### Step 10: Password Change (Domain Method)
```python
# File: apps/user_management/domain/entities/user.py
user.change_password(
    old_password=command.old_password,
    new_password=command.new_password,
    password_hasher=self._password_service
)

# Inside User.change_password():
# 1. Verify old password matches current
# 2. Validate new password meets policy
# 3. Hash new password
# 4. Update password_hash
# 5. Update timestamp
# 6. Generate UserPasswordChanged domain event
```

#### Step 11: Password Verification
```python
# File: apps/user_management/domain/entities/user.py
if not self._password_hasher.verify(self.password_hash, old_password):
    raise InvalidCredentialsError("Current password is incorrect")
```

#### Step 12: New Password Hashing
```python
# File: apps/user_management/infrastructure/auth/bcrypt_hasher.py
new_hash = self._password_hasher.hash(new_password)
self.password_hash = PasswordHash(new_hash)
```

#### Step 13: Domain Event Generation
```python
# File: apps/user_management/domain/entities/user.py
password_changed_event = UserPasswordChanged(
    event_id=str(uuid.uuid4()),
    occurred_at=datetime.utcnow(),
    user_data={...}
)
```

### 🔧 **Infrastructure Layer Flow**

#### Step 14: User Persistence
```python
self._user_repository.update(user)
```

#### Step 15: Event Persistence
```python
# File: apps/user_management/infrastructure/outbox/writer.py
for event in change_result.events:
    write_domain_event(event)
```

### 🎯 **Presentation Layer Response**

#### Step 16: Success Response
```python
return Response(
    {"message": "Password changed successfully"},
    status=status.HTTP_200_OK
)
```

### 📡 **HTTP Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Password changed successfully"
}
```

---

## 🔄 Use Case Flow #6: Deactivate User Account

### 📡 **HTTP Request Entry**
```http
POST /api/v1/users/profile/deactivate/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "reason": "User requested account closure"
}
```

### 🎯 **Presentation Layer Flow**

#### Step 1-5: Authentication Flow
*Same as Get Current User Profile (Steps 1-5)*

#### Step 6: Request Validation
```python
# File: apps/user_management/presentation/serializers.py
serializer = DeactivateUserSerializer(data=request.data)
# Validates optional reason field
```

#### Step 7: Command Creation
```python
deactivate_command = DeactivateUserCommand(
    user_id=str(current_user.id.value),
    reason=serializer.validated_data.get('reason'),
)
```

### 📋 **Application Layer Flow**

#### Step 8: Handler Execution
```python
# File: apps/user_management/application/handlers/deactivate_user.py
def handle(self, command: DeactivateUserCommand) -> DeactivateUserResult:
```

#### Step 9: User Lookup
```python
user_id = UserId.from_string(command.user_id)
user = self._user_repository.find_by_id(user_id)
```

### 🏛️ **Domain Layer Flow**

#### Step 10: User Deactivation (Domain Method)
```python
# File: apps/user_management/domain/entities/user.py
user.deactivate(reason=command.reason)

# Inside User.deactivate():
# 1. Check if user is already deactivated
# 2. Set status to INACTIVE
# 3. Update timestamp
# 4. Generate UserDeactivated domain event with reason
```

#### Step 11: Domain Event Generation
```python
# File: apps/user_management/domain/entities/user.py
user_deactivated_event = UserDeactivated(
    event_id=str(uuid.uuid4()),
    occurred_at=datetime.utcnow(),
    user_data={...},
    reason=reason
)
```

### 🔧 **Infrastructure Layer Flow**

#### Step 12: User Persistence
```python
self._user_repository.save(user)
```

#### Step 13: Event Persistence
```python
# File: apps/user_management/infrastructure/outbox/writer.py
for event in deactivate_result.events:
    write_domain_event(event)
```

### 🎯 **Presentation Layer Response**

#### Step 14: Success Response
```python
return Response(
    {"message": "Account deactivated successfully"},
    status=status.HTTP_200_OK
)
```

### 📡 **HTTP Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Account deactivated successfully"
}
```

---

## 🚨 Error Flow Examples

### ❌ **Validation Error Flow**

#### Step 1: Invalid Request
```http
POST /api/v1/users/auth/register/
Content-Type: application/json

{
  "email": "invalid-email",
  "password": "123",
  "first_name": "",
  "last_name": "Doe"
}
```

#### Step 2: Serializer Validation Failure
```python
# File: apps/user_management/presentation/serializers.py
# Email format validation fails
# Password too short
# First name empty
```

#### Step 3: Error Response
```python
return Response(
    {"error": "Validation failed", "details": serializer.errors},
    status=status.HTTP_400_BAD_REQUEST
)
```

#### Step 4: HTTP Error Response
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Validation failed",
  "details": {
    "email": ["Enter a valid email address."],
    "password": ["Ensure this field has at least 8 characters."],
    "first_name": ["This field may not be blank."]
  }
}
```

### ❌ **Domain Error Flow**

#### Step 1: Business Rule Violation
```python
# File: apps/user_management/application/handlers/register_user.py
# User already exists with same email
existing_user = self._user_repository.find_by_email(email)
if existing_user is not None:
    raise UserAlreadyExistsError(email.value)
```

#### Step 2: Error Translation
```python
# File: apps/user_management/presentation/views.py
except (UserAlreadyExistsError, PasswordPolicyError, DomainValidationError) as e:
    return _handle_domain_errors(e)
```

#### Step 3: HTTP Error Response
```http
HTTP/1.1 409 Conflict
Content-Type: application/json

{
  "error": "User with this email already exists",
  "code": "USER_ALREADY_EXISTS"
}
```

### ❌ **Authentication Error Flow**

#### Step 1: Invalid Credentials
```python
# File: apps/user_management/application/handlers/authenticate_user.py
is_valid = user.verify_password(command.password, self._password_service)
if not is_valid:
    raise InvalidCredentialsError("Invalid email or password")
```

#### Step 2: HTTP Error Response
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
}
```

---

## 📊 System Integration Points

### 🔗 **Cross-Layer Dependencies**

```mermaid
graph TD
    A[HTTP Request] --> B[Presentation Layer]
    B --> C[Application Layer]
    C --> D[Domain Layer]
    C --> E[Infrastructure Layer]
    E --> F[Database]
    E --> G[Outbox Events]
    
    B --> H[Authentication Middleware]
    H --> I[JWT Verification]
    I --> E
    
    C --> J[Event Publishing]
    J --> E
```

### 🎯 **Key Integration Patterns**

1. **Dependency Injection**: Infrastructure container resolves dependencies
2. **Event-Driven Architecture**: Domain events → Outbox → Background processing
3. **Clean Architecture**: Layers depend only inward, never outward
4. **Repository Pattern**: Domain uses interfaces, infrastructure provides implementations
5. **DTO Pattern**: Data transfer between layers without coupling
6. **Command Pattern**: Use case inputs as immutable commands
7. **Authentication**: JWT middleware → User lookup → Request context

### 🔄 **Event Flow (Async Background Processing)**

```mermaid
sequenceDiagram
    participant U as User Action
    participant P as Presentation
    participant A as Application  
    participant D as Domain
    participant I as Infrastructure
    participant O as Outbox
    participant B as Background Processor
    
    U->>P: HTTP Request
    P->>A: Execute Command
    A->>D: Business Logic
    D->>D: Generate Domain Event
    A->>I: Persist User
    A->>O: Write Events to Outbox
    P->>U: HTTP Response
    
    Note over B: Separate Process
    B->>O: Poll for Events
    O->>B: Return Unprocessed Events
    B->>B: Process Events
    B->>O: Mark as Processed
```

This comprehensive flow documentation shows how every use case traverses the entire system architecture, maintaining clean separation of concerns while providing complete end-to-end functionality.