# 📘 Documentation: UserManagement Bounded Context  

## 1. Purpose & Scope
The **UserManagement bounded context** handles user identity and authentication within the expense tracking system.  

- Provides account creation, login, and profile management.  
- Issues and verifies JWT tokens for authentication.  
- Exposes `UserId` for use in other bounded contexts (e.g., ExpenseManagement).  
- No roles, permissions, or advanced features — flat user model only.  

---

## 2. Constraints & Guiding Principles
- **KISS (Keep It Simple, Stupid):** only implement essential features (registration, login, profile, password, deactivation).  
- **Separation of Concerns:**  
  - Presentation (API endpoints)  
  - Application (use cases/handlers)  
  - Domain (entities, value objects, services, repositories)  
  - Infrastructure (DB, JWT, hashing)  
- **Modular Monolith:** internal communication between bounded contexts (direct calls, no APIs/events).  
- **Time Constraint:** 1-week MVP, 4-person team → only core features.  
- **Security Constraint:**  
  - Passwords always hashed (bcrypt).  
  - JWT tokens used for session/auth.  

---

## 3. Functional Requirements
- Register a new user (email, password, name).  
- Authenticate existing user (login with email & password).  
- Update user profile (email, name).  
- Change password (with old password check).  
- Deactivate user account (soft delete).  

---

## 4. User Stories  

### Registration
- **As a** new user  
- **I want** to register with my email, password, and optional name  
- **So that** I can create an account and start tracking expenses  

**Acceptance Criteria:**  
- Unique email  
- Password stored securely  
- Confirmation returned  

### Login
- **As a** registered user  
- **I want** to log in with my email and password  
- **So that** I can access my account securely  

**Acceptance Criteria:**  
- Valid credentials return JWT  
- Invalid credentials return error  

### Update Profile
- **As a** logged-in user  
- **I want** to update my name or email  
- **So that** my account details remain current  

**Acceptance Criteria:**  
- Email remains unique  
- Only self can update  

### Change Password
- **As a** logged-in user  
- **I want** to change my password using my current one  
- **So that** I can maintain account security  

**Acceptance Criteria:**  
- Must verify old password  
- New password hashed before saving  

### Deactivate Account
- **As a** logged-in user  
- **I want** to deactivate my account  
- **So that** I can stop using the app and remove access  

**Acceptance Criteria:**  
- Account marked inactive  
- No further login allowed  

---

## 5. User Flows  

### 5.1 Registration Flow
```
User → API /auth/register → RegisterUserHandler → UserService.register()
  → Password.hash → UserRepository.save() → Success response
```

### 5.2 Login Flow
```
User → API /auth/login → AuthenticateUserHandler → UserService.authenticate()
  → UserRepository.findByEmail() → Password.verify → AuthService.signToken()
  → JWT returned to user
```

### 5.3 Profile Update Flow
```
User → API /users/me (PUT) → UpdateUserProfileHandler → UserService.updateProfile()
  → UserRepository.update() → Success response
```

### 5.4 Change Password Flow
```
User → API /users/me/password (PUT) → ChangePasswordHandler
  → UserService.changePassword() → Password.verify → Password.hash
  → UserRepository.update() → Success response
```

### 5.5 Deactivation Flow
```
User → API /users/me (DELETE) → DeactivateUserHandler
  → UserService.deactivateUser() → UserRepository.update()
  → Success response
```

---

## 6. Domain Model (UML Overview)
```plaintext
+-------------------+
|      User         |
+-------------------+
| - userId: UserId  |
| - email: Email    |
| - password: Password |
| - name: String?   |
| - createdAt: Date |
+-------------------+
| + updateProfile(newEmail: Email, newName: String) |
| + changePassword(oldPassword: String, newPassword: String) |
| + deactivate() |
+-------------------+

+-------------------+
|      Email        |
+-------------------+
| - value: String   |
+-------------------+
| + isValid(): Boolean |
| + equals(other: Email): Boolean |
+-------------------+

+-------------------+
|     Password      |
+-------------------+
| - hash: String    |
+-------------------+
| + verify(plain: String): Boolean |
| + fromPlain(plain: String): Password (static factory) |
+-------------------+

+-------------------+
|     UserId        |
+-------------------+
| - value: UUID     |
+-------------------+

+-------------------+
|   UserService     |
+-------------------+
| + register(email, password, name) |
| + authenticate(email, password) |
| + updateProfile(userId, name, email?) |
| + changePassword(userId, oldPass, newPass) |
| + deactivateUser(userId) |
+-------------------+

+-------------------+
|   AuthService     | (Interface)
+-------------------+
| + hashPassword(plain): String |
| + verifyPassword(hash, plain): Boolean |
| + signToken(user): String |
| + verifyToken(token): UserId |
+-------------------+

+-------------------+
| UserRepository    | (Interface)
+-------------------+
| + findByEmail(email: Email): User? |
| + findById(userId: UserId): User? |
| + save(user: User) |
| + update(user: User) |
+-------------------+
```

---

## 7. Database Schema
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);
```

---

## 8. API Endpoints
- `POST /auth/register` → register user  
- `POST /auth/login` → login, returns JWT  
- `PUT /users/me` → update profile (requires JWT)  
- `PUT /users/me/password` → change password (requires JWT)  
- `DELETE /users/me` → deactivate account (requires JWT)  

---

## 9. Responsibilities & Module Boundaries
- **Domain layer:** `User`, `Email`, `Password`, `UserId`, `UserService`  
- **Application layer:** Handlers for each use case (RegisterUserHandler, etc.)  
- **Infrastructure layer:**  
  - `UserRepositoryImpl` (SQL/ORM)  
  - `AuthServiceImpl` (bcrypt + JWT)  
- **Presentation layer:** REST controllers mapping HTTP → application handlers  
