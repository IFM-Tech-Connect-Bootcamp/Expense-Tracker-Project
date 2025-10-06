# 📘 Documentation: ExpenseManagement Bounded Context

## 1. Purpose & Scope

The **ExpenseManagement bounded context** handles all features related to expense tracking within the system.

- Allows users to create, view, update, and delete expenses.
- Each expense belongs to exactly one user and one category.
- Provides expense categorization and filtering.
- Enables viewing total expenses (summary reports).
- Simple MVP — no recurring expenses, receipt uploads, or advanced analytics.
- **Currency is fixed to Tanzanian Shillings (TZS).**

---

## 2. Constraints & Guiding Principles

- **KISS:** only implement basic CRUD + simple reporting.
- **Separation of Concerns:** same layering as UserManagement (presentation, application, domain, infrastructure).
- **Modular Monolith:** communicates internally with UserManagement (via direct calls using `UserId`).
- **MVP Scope:** must be fully buildable within 1 week by a 4-person team.
- **Data Integrity:**
  - Expense must belong to a valid user.
  - Expense must belong to a valid category.
  - Expense amounts always in **TZS**.

---

## 3. Functional Requirements

- Add a new expense (amount in TZS, description, category, date).
- Update an existing expense.
- Delete an expense.
- View expenses (all, by category, by date range).
- View summary totals (overall or by category).
- Manage categories (add, update, delete, list).

---

## 4. User Stories

### Add Expense

- **As a** logged-in user
- **I want** to add a new expense with amount (TZS), description, category, and date
- **So that** I can track my spending

**Acceptance Criteria:**

- Expense stored with a valid category & userId
- Default to today’s date if none given

### Update Expense

- **As a** logged-in user
- **I want** to update details of an existing expense
- **So that** I can correct mistakes or add more detail

**Acceptance Criteria:**

- User can only update their own expenses

### Delete Expense

- **As a** logged-in user
- **I want** to delete an expense
- **So that** I can remove incorrect or unwanted records

**Acceptance Criteria:**

- User can only delete their own expenses

### View Expenses

- **As a** logged-in user
- **I want** to view a list of my expenses
- **So that** I can review my spending history

**Acceptance Criteria:**

- Filter by date range or category
- Sorted by date (default: latest first)

### Summary Totals

- **As a** logged-in user
- **I want** to see the total amount spent overall and by category (in TZS)
- **So that** I can understand my spending patterns

**Acceptance Criteria:**

- Returns aggregate numbers per user
- Always expressed in TZS

### Manage Categories

- **As a** logged-in user
- **I want** to create, edit, and delete categories
- **So that** I can organize my expenses meaningfully

**Acceptance Criteria:**

- Each category belongs to one user
- Default categories provided on first registration

---

## 5. User Flows

### 5.1 Add Expense Flow

```
User → API /expenses (POST) → AddExpenseHandler → ExpenseService.addExpense()
  → ExpenseRepository.save() → Success response
```

### 5.2 View Expenses Flow

```
User → API /expenses (GET) → GetExpensesHandler → ExpenseService.listExpenses()
  → ExpenseRepository.findByUser(userId) → Return list
```

### 5.3 Update Expense Flow

```
User → API /expenses/{id} (PUT) → UpdateExpenseHandler → ExpenseService.updateExpense()
  → ExpenseRepository.findById() → Save changes
```

### 5.4 Delete Expense Flow

```
User → API /expenses/{id} (DELETE) → DeleteExpenseHandler
  → ExpenseService.deleteExpense() → ExpenseRepository.delete()
```

### 5.5 Manage Categories Flow

```
User → API /categories (CRUD endpoints) → CategoryHandlers → CategoryService
  → CategoryRepository
```

---

## 6. Domain Model (UML Overview)

```plaintext
+-------------------+
|     Expense       |
+-------------------+
| - expenseId: ExpenseId |
| - userId: UserId       |
| - categoryId: CategoryId |
| - amountTZS: Decimal  |
| - description: String? |
| - date: Date           |
+-------------------+
| + update(amountTZS, description, category, date) |
| + belongsTo(userId: UserId): Boolean             |
+-------------------+

+-------------------+
|    Category       |
+-------------------+
| - categoryId: CategoryId |
| - userId: UserId         |
| - name: String           |
+-------------------+
| + rename(newName: String) |
| + belongsTo(userId: UserId): Boolean |
+-------------------+

+-------------------+
|   ExpenseService  |
+-------------------+
| + addExpense(userId, amountTZS, description, category, date) |
| + updateExpense(expenseId, userId, changes) |
| + deleteExpense(expenseId, userId) |
| + listExpenses(userId, filters) |
| + getSummary(userId) |
+-------------------+

+-------------------+
| CategoryService   |
+-------------------+
| + addCategory(userId, name) |
| + renameCategory(categoryId, userId, newName) |
| + deleteCategory(categoryId, userId) |
| + listCategories(userId) |
+-------------------+

+-------------------+
| ExpenseRepository | (Interface)
+-------------------+
| + save(expense: Expense) |
| + findById(expenseId: ExpenseId): Expense? |
| + findByUser(userId: UserId): List<Expense> |
| + delete(expense: Expense) |
+-------------------+

+-------------------+
| CategoryRepository | (Interface)
+-------------------+
| + save(category: Category) |
| + findById(categoryId: CategoryId): Category? |
| + findByUser(userId: UserId): List<Category> |
| + delete(category: Category) |
+-------------------+
```

---

## 7. Database Schema

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

---

## 8. API Endpoints

### Expenses

- `POST /expenses` → add expense (amount in TZS)
- `GET /expenses` → list expenses (filter by date/category optional)
- `PUT /expenses/{id}` → update expense
- `DELETE /expenses/{id}` → delete expense
- `GET /expenses/summary` → get totals (TZS only)

### Categories

- `POST /categories` → add category
- `GET /categories` → list categories
- `PUT /categories/{id}` → rename category
- `DELETE /categories/{id}` → delete category

---

## 9. Responsibilities & Module Boundaries

- **Domain layer:** `Expense`, `Category`, services, value objects
- **Application layer:** Handlers (`AddExpenseHandler`, `UpdateExpenseHandler`, etc.)
- **Infrastructure layer:**
  - `ExpenseRepositoryImpl` (SQL/ORM)
  - `CategoryRepositoryImpl` (SQL/ORM)
- **Presentation layer:** REST controllers mapping HTTP → application handlers

