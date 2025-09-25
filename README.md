# 📘 Project Documentation: Personal Expense Tracker

## 1. Overview
The **Personal Expense Tracker** is a modular monolith system designed to help users track their expenses in Tanzanian Shillings (TZS). The project is structured using **Domain-Driven Design (DDD)** principles, with a focus on simplicity (KISS), modularity, and a clear separation of concerns.

The system is split into two bounded contexts (modules):
1. **UserManagement** – handles authentication, user accounts, and identity.
2. **ExpenseManagement** – manages expenses, categories, and summaries.

This document serves as the **initial README** for the project, providing a full breakdown of requirements, scope, design, and architecture.

---

## 2. Project Goals
- Allow users to create and manage personal accounts.
- Enable users to track expenses in **TZS** with categories.
- Provide summaries and filtering for spending insights.
- Deliver an MVP within **1 week** (4-person team, 5 working days + 1 buffer).
- Ensure maintainability and simplicity through modular DDD.

---

## 3. Constraints, Design Principles & Guidelines
- **KISS (Keep It Simple, Stupid):** implement only necessary MVP features, no premature optimization.
- **Separation of Concerns:** clear layered architecture (presentation, application, domain, infrastructure). Each layer has a single responsibility.
- **Domain-Driven Design (DDD):** organize the system into bounded contexts (UserManagement, ExpenseManagement) with rich domain models and services.
- **Modular Monolith:** bounded contexts communicate internally via direct calls, not external APIs.
- **MVP Scope:** must be achievable within 1 week by a 4-person team (5 working days + 1 buffer day).
- **Maintainability:** modular codebase with clear boundaries, enabling future extension without heavy refactoring.
- **Currency Constraint:** all expenses are tracked in Tanzanian Shillings (TZS) only, avoiding multi-currency complexity.
- **Security:** passwords hashed, token-based authentication, and access control per user.
- **Deliverables:** backend repo (REST API), frontend repo (SPA), README/docs, deployment, tests, and simple CI/CD pipeline.

---

## 4. Domain Breakdown

### 4.1 UserManagement Bounded Context
**Purpose:** Handle user authentication, registration, and identity management.

**Features:**
- User registration (email + password).
- User login (token-based authentication).
- User profile management (basic account info).

**Domain Model (simplified UML):**
```plaintext
+------------+       +---------------+
|   User     |       |   UserService |
+------------+       +---------------+
| - userId   |       | + register()  |
| - email    |       | + login()     |
| - password |       | + updateUser()|
+------------+       +---------------+
```

**Database Schema:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API Endpoints:**
- `POST /users/register` → register user
- `POST /users/login` → login and get token
- `GET /users/me` → view profile

---

### 4.2 ExpenseManagement Bounded Context
**Purpose:** Allow users to track expenses and categorize them.

**Features:**
- Add, update, delete expenses.
- Filter expenses by date and category.
- Manage categories (CRUD).
- View summary totals in TZS.

**Domain Model (simplified UML):**
```plaintext
+-------------------+        +-------------------+
|     Expense       |        |   ExpenseService  |
+-------------------+        +-------------------+
| - expenseId       |        | + addExpense()    |
| - userId          |        | + updateExpense() |
| - categoryId      |        | + deleteExpense() |
| - amountTZS       |        | + listExpenses()  |
| - description     |        | + getSummary()    |
| - date            |        +-------------------+
+-------------------+

+-------------------+        +-------------------+
|    Category       |        | CategoryService   |
+-------------------+        +-------------------+
| - categoryId      |        | + addCategory()   |
| - userId          |        | + renameCategory()|
| - name            |        | + deleteCategory()|
+-------------------+        | + listCategories()|
                             +-------------------+
```

**Database Schema:**
```sql
CREATE TABLE categories (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  name VARCHAR(100) NOT NULL,
  UNIQUE(user_id, name)
);

CREATE TABLE expenses (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  category_id UUID NOT NULL REFERENCES categories(id),
  amount_tzs DECIMAL(10,2) NOT NULL,
  description TEXT,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API Endpoints:**
- `POST /expenses` → add expense (TZS only)
- `GET /expenses` → list expenses (filters optional)
- `PUT /expenses/{id}` → update expense
- `DELETE /expenses/{id}` → delete expense
- `GET /expenses/summary` → totals in TZS
- `POST /categories` → add category
- `GET /categories` → list categories
- `PUT /categories/{id}` → rename category
- `DELETE /categories/{id}` → delete category

---

## 5. User Stories (Summary)

### UserManagement
- Register account with email + password.
- Login and receive token.
- View account details.

### ExpenseManagement
- Add expense in TZS.
- Update or delete expense.
- View all expenses with filters.
- View summary totals.
- Manage categories.

---

## 6. Project Deliverables
- **Backend repo:** REST API with modular monolith structure.
- **Frontend repo:** SPA consuming the API.
- **Documentation:** README (this file), plus module docs.
- **Deployment:** basic staging URL.
- **Tests:** automated unit and integration tests.
- **CI/CD:** simple pipeline.

---

## 7. Architecture Summary
- **Presentation layer:** REST controllers.
- **Application layer:** use-case handlers.
- **Domain layer:** entities, value objects, services.
- **Infrastructure layer:** repositories (SQL/ORM).

---