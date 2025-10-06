# Expense Management Domain Layer Implementation

## Overview

I have successfully implemented a complete, clean, DRY, and strictly typed domain layer for the Expense Management bounded context. The implementation follows Domain-Driven Design (DDD) principles and Clean Architecture patterns. Please use this as your guide to understand the domain layer. Furthermore, each file contains explicit documentation to help you understand what is going on. All the best!

## 🏗️ Architecture & Structure

The domain layer is organized as follows:

```
expense_management/domain/
├── __init__.py                 # Main exports and API
├── value_objects/              # Value objects (immutable, validated)
│   ├── expense_id.py          # UUID wrapper for expense identification
│   ├── category_id.py         # UUID wrapper for category identification
│   ├── user_id.py             # UUID wrapper for user identification (shared)
│   ├── amount_tzs.py          # Tanzanian Shillings amount validation
│   ├── expense_description.py # Expense description validation
│   └── category_name.py       # Category name validation and normalization
├── entities/                   # Domain entities (business logic)
│   ├── expense.py             # Expense aggregate root
│   └── category.py            # Category aggregate root
├── enums/                      # Domain enumerations
│   └── expense_status.py      # Expense status lifecycle
├── events/                     # Domain events
│   ├── expense_events.py      # Expense-related domain events
│   └── category_events.py     # Category-related domain events
├── services/                   # Domain service interfaces
│   ├── expense_summary_service.py      # Expense calculation and aggregation
│   ├── category_validation_service.py  # Category business rules
│   └── default_category_service.py     # Default category management
├── repositories/               # Repository interfaces
│   ├── expense_repository.py   # Expense persistence contract
│   └── category_repository.py  # Category persistence contract
└── errors.py                   # Domain-specific exceptions
```

## 🎯 Key Features & Principles

### 1. **Framework-Agnostic Design**
- Zero Django imports in domain layer
- Pure Python with standard library only
- Easily testable and portable
- Clear separation of concerns

### 2. **Strictly Typed Implementation**
- Type hints throughout using `typing` module
- Protocol-based interfaces for dependency injection
- Generic types where appropriate
- Type safety at compile time

### 3. **Synchronous Architecture**
- Direct method calls without async complexity
- Standard Python patterns for easier team adoption
- Simplified debugging and error tracking
- Improved maintainability for teams unfamiliar with async

### 4. **DRY (Don't Repeat Yourself)**
- Shared base classes and protocols
- Reusable validation patterns
- Common error handling strategies
- Consistent naming conventions

### 5. **Clean Code Practices**
- Comprehensive docstrings
- Single Responsibility Principle
- Descriptive method and variable names
- Proper exception handling

### 6. **TZS Currency Focus**
- Native Tanzanian Shillings support
- Proper decimal handling for currency
- Built-in validation and formatting
- Currency-specific business rules

## 🔧 Core Components

### Value Objects

#### `ExpenseId`
- Wraps UUID for type safety
- Factory methods for creation and parsing
- Immutable and hashable
- String conversion support

#### `CategoryId`
- Wraps UUID for type safety
- Factory methods for creation and parsing
- Immutable and hashable
- String conversion support

#### `UserId`
- Shared value object from User Management context
- UUID wrapper for cross-context user identification
- Type safety for user references
- String conversion and parsing support

#### `AmountTZS`
- Validates Tanzanian Shillings amounts
- Decimal precision for currency accuracy
- Arithmetic operations (add, subtract, multiply, divide)
- Automatic formatting and validation
- Zero amount support and detection
- Comparison operations for sorting and filtering

#### `ExpenseDescription`
- Optional expense description validation
- Length validation (500 characters max)
- Automatic normalization (trim whitespace)
- Empty string handling (converts to None)
- Type safety for description operations

#### `CategoryName`
- Category name validation (100 characters max)
- Automatic normalization (trim whitespace)
- Required field validation
- Type safety for category operations

### Entities

#### `Expense` (Aggregate Root)

##### Core Behavior
- **Amount Management**: Update expense amounts with validation
- **Description Operations**: Manage optional expense descriptions
- **Category Assignment**: Change expense categorization
- **Date Management**: Update expense dates
- **Ownership Validation**: Verify user ownership
- **Event Publishing**: Domain event generation for changes
- **Filtering Support**: Date range and category filtering

##### Business Rules
- Expenses must belong to a valid user
- Expenses must have a valid category
- Amounts must be in Tanzanian Shillings (TZS)
- Amounts must be non-negative
- Users can only access their own expenses
- All changes are tracked with timestamps
- Domain events are published for significant changes

#### `Category` (Aggregate Root)

##### Core Behavior
- **Name Management**: Update category names with validation
- **Ownership Validation**: Verify user ownership
- **Event Publishing**: Domain event generation
- **Uniqueness Support**: Per-user category name uniqueness

##### Business Rules
- Categories must belong to a valid user
- Category names must be unique per user
- Category names are required and validated
- Users can only access their own categories
- Categories cannot be deleted if expenses exist
- All changes are tracked with timestamps

### Domain Events

#### Expense Events
- `ExpenseCreated`: New expense creation
- `ExpenseUpdated`: Expense modifications
- `ExpenseDeleted`: Expense removal

#### Category Events
- `CategoryCreated`: New category creation
- `CategoryUpdated`: Category modifications
- `CategoryDeleted`: Category removal

#### Event Features
- Immutable event objects
- Structured event data with TZS amounts
- Event versioning support
- Dictionary serialization
- Aggregate identification

### Domain Services

#### `ExpenseSummaryService`
- **Pure Business Logic**: Static methods for calculations
- **Total Calculations**: Sum expenses by various criteria
- **Category Aggregation**: Group and sum by categories
- **Average Calculations**: Compute average expense amounts
- **Count Operations**: Count expenses by criteria
- **Currency Handling**: Native TZS amount operations

#### `CategoryValidationService`
- **Uniqueness Validation**: Ensure category names are unique per user
- **Ownership Validation**: Verify category belongs to user
- **Business Rule Enforcement**: Category-specific validations
- **Name Format Validation**: Proper category name format

#### `DefaultCategoryService`
- **Default Categories**: Predefined category list for new users
- **Category Creation**: Generate default categories
- **Validation Support**: Check for default category presence
- **Minimum Category Rules**: Ensure users have required categories

### Repository Interfaces

#### `ExpenseRepository`
- Complete CRUD operations for expenses
- User-based filtering and queries
- Category-based filtering
- Date range queries
- Combined filtering (user + category + date)
- Existence checking and counting
- Synchronous operations for team maintainability

#### `CategoryRepository`
- Complete CRUD operations for categories
- User-based filtering
- Name uniqueness checking
- Usage validation (expenses dependency)
- Existence checking and counting
- Synchronous operations for maintainability

## 🚀 Business Logic Implementation

### Expense Creation Flow
```python
expense = Expense.create(
    user_id=UserId.from_string("user-uuid"),
    category_id=CategoryId.from_string("category-uuid"),
    amount_tzs=AmountTZS.from_float(15000.50),
    description=ExpenseDescription.from_string("Grocery shopping at Shoprite"),
    expense_date=date.today()
)
# Automatically publishes ExpenseCreated event with TZS amount
```

### Expense Update Flow
```python
expense.update(
    amount_tzs=AmountTZS.from_float(18000.00),
    description=ExpenseDescription.from_string("Updated: Grocery shopping with extras"),
    category_id=new_category_id
)
# Validates business rules and publishes ExpenseUpdated event
```

### Category Creation Flow
```python
category = Category.create(
    user_id=UserId.from_string("user-uuid"),
    name=CategoryName.from_string("Food & Dining")
)
# Automatically publishes CategoryCreated event
```

### Default Categories Setup Flow
```python
default_categories = DefaultCategoryService.create_default_categories_for_user(user_id)
# Creates 10 default categories: Food & Dining, Transportation, Shopping, etc.
```

### Expense Summary Calculations
```python
# Calculate total spending
total = ExpenseSummaryService.calculate_total_amount(user_expenses)

# Calculate spending by category
category_totals = ExpenseSummaryService.calculate_total_by_category(user_expenses)

# Calculate average expense
average = ExpenseSummaryService.calculate_average_expense_amount(user_expenses)
```

## 🛡️ Error Handling

### Domain-Specific Exceptions
- `ExpenseNotFoundError`: Missing expense operations
- `ExpenseAccessDeniedError`: Unauthorized expense access
- `InvalidExpenseDataError`: Expense validation failures
- `CategoryNotFoundError`: Missing category operations
- `CategoryAccessDeniedError`: Unauthorized category access
- `DuplicateCategoryNameError`: Category name conflicts
- `CategoryInUseError`: Delete operations on used categories
- `InvalidCategoryDataError`: Category validation failures
- `UserNotFoundError`: Missing user references
- `BusinessRuleViolationError`: General business rule violations
- `ValidationError`: General validation failures

### Error Design
- Structured error messages with TZS context
- Optional error details dictionary
- Clear error classification
- Exception chaining support
- Business rule violation tracking

## 📋 Validation & Invariants

### Amount Validation (TZS)
- Non-negative amounts enforced
- Two decimal place precision
- Proper Decimal type usage
- Currency formatting support
- Arithmetic operation validation

### Description Validation
- Optional field handling
- Length restrictions (500 chars)
- Automatic normalization
- Empty string to None conversion

### Category Name Validation
- Required field validation
- Length restrictions (100 chars)
- Character validation and normalization
- Uniqueness per user enforcement

### Expense Entity Invariants
- Valid user ownership required
- Valid category assignment required
- TZS amount constraints
- Consistent timestamp ordering
- Business rule compliance

### Category Entity Invariants
- Valid user ownership required
- Unique names per user
- Required name validation
- Deletion protection when in use

## 🎯 Domain Events

### Event Structure
- Unique event identifiers
- Timestamp tracking
- Aggregate identification
- TZS amount tracking for financial events
- Version management
- Structured event data

### Event Usage
- Financial audit trail creation
- Inter-context communication
- Integration with User Management
- State change notifications
- Expense tracking and reporting

## 💰 TZS Currency Features

### Native Currency Support
- **TZS-First Design**: All amounts in Tanzanian Shillings
- **Decimal Precision**: Proper currency math with 2 decimal places
- **Formatting**: "TZS 15,000.50" display format
- **Validation**: Currency-specific validation rules
- **Arithmetic**: Safe currency operations (add, subtract, multiply, divide)
- **Comparison**: Proper currency comparison operations

### Business Rules
- All amounts must be in TZS
- No negative amounts allowed
- Proper decimal precision enforced
- Currency formatting standardized
- Mathematical operations validated

## 🏆 Benefits

### For Development Team
- **Type Safety**: Catch errors at compile time with TZS amounts
- **Testability**: Easy unit testing without infrastructure
- **Maintainability**: Clear domain boundaries and responsibilities
- **Extensibility**: Protocol-based design for easy extension
- **Currency Safety**: TZS-specific validation and operations

### For Business
- **Financial Accuracy**: Precise TZS currency handling
- **Auditability**: Complete expense and category tracking
- **Data Integrity**: Comprehensive validation and error handling
- **User Experience**: Proper category management and expense organization
- **Scalability**: Clean architecture for future enhancements

### For Tanzanian Market
- **Local Currency**: Native TZS support without conversion
- **Cultural Relevance**: Default categories relevant to local context
- **Compliance**: Proper currency handling for local regulations
- **User Familiarity**: TZS-native interface and calculations

## 📊 Default Categories

The system provides 10 default categories for new users:
1. **Food & Dining** - Restaurant meals, groceries, food delivery
2. **Transportation** - Fuel, public transport, vehicle maintenance
3. **Shopping** - Clothing, electronics, general purchases
4. **Entertainment** - Movies, events, recreational activities
5. **Bills & Utilities** - Electricity, water, internet, phone bills
6. **Health & Medical** - Doctor visits, medicines, health insurance
7. **Travel** - Hotels, flights, vacation expenses
8. **Education** - School fees, books, courses, training
9. **Personal Care** - Haircuts, cosmetics, personal hygiene
10. **Other** - Miscellaneous expenses that don't fit other categories

## 🔄 Integration with User Management

### Shared Concepts
- **UserId**: References users from User Management context
- **Event System**: Compatible event patterns for integration
- **Error Handling**: Consistent error patterns across contexts
- **Repository Patterns**: Same interface design principles

### Bounded Context Boundaries
- Clear separation between user and expense concerns
- Shared identifiers without tight coupling
- Independent business rules and validation
- Autonomous deployment and scaling capabilities