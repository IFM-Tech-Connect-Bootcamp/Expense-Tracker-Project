"""Domain-specific exceptions for Expense Management.

This module contains all the domain-level exceptions that can be raised
during expense management operations. These exceptions represent business
rule violations and domain invariant failures.
"""

from typing import Any, Optional


class ExpenseManagementDomainError(Exception):
    """Base exception for all expense management domain errors.
    
    This is the base class for all domain-specific exceptions in the
    expense management bounded context.
    """
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the domain error.
        
        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ExpenseError(ExpenseManagementDomainError):
    """Base exception for expense-related errors."""
    pass


class ExpenseNotFoundError(ExpenseError):
    """Raised when an expense cannot be found."""
    
    def __init__(self, expense_id: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Expense with ID {expense_id} not found"
        super().__init__(message, details)
        self.expense_id = expense_id


class ExpenseAccessDeniedError(ExpenseError):
    """Raised when a user tries to access an expense they don't own."""
    
    def __init__(self, expense_id: str, user_id: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"User {user_id} does not have access to expense {expense_id}"
        super().__init__(message, details)
        self.expense_id = expense_id
        self.user_id = user_id


class InvalidExpenseDataError(ExpenseError):
    """Raised when expense data is invalid."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(f"Invalid expense data: {message}", details)


class CategoryError(ExpenseManagementDomainError):
    """Base exception for category-related errors."""
    pass


class CategoryNotFoundError(CategoryError):
    """Raised when a category cannot be found."""
    
    def __init__(self, category_id: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Category with ID {category_id} not found"
        super().__init__(message, details)
        self.category_id = category_id


class CategoryAccessDeniedError(CategoryError):
    """Raised when a user tries to access a category they don't own."""
    
    def __init__(self, category_id: str, user_id: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"User {user_id} does not have access to category {category_id}"
        super().__init__(message, details)
        self.category_id = category_id
        self.user_id = user_id


class DuplicateCategoryNameError(CategoryError):
    """Raised when trying to create a category with a name that already exists for the user."""
    
    def __init__(self, name: str, user_id: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Category '{name}' already exists for user {user_id}"
        super().__init__(message, details)
        self.name = name
        self.user_id = user_id


class CategoryInUseError(CategoryError):
    """Raised when trying to delete a category that has expenses associated with it."""
    
    def __init__(self, category_id: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Cannot delete category {category_id} because it has associated expenses"
        super().__init__(message, details)
        self.category_id = category_id


class InvalidCategoryDataError(CategoryError):
    """Raised when category data is invalid."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(f"Invalid category data: {message}", details)


class UserNotFoundError(ExpenseManagementDomainError):
    """Raised when a referenced user cannot be found."""
    
    def __init__(self, user_id: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"User with ID {user_id} not found"
        super().__init__(message, details)
        self.user_id = user_id


class BusinessRuleViolationError(ExpenseManagementDomainError):
    """Raised when a business rule is violated."""
    
    def __init__(self, rule: str, message: str, details: Optional[dict[str, Any]] = None) -> None:
        full_message = f"Business rule violation ({rule}): {message}"
        super().__init__(full_message, details)
        self.rule = rule


class ValidationError(ExpenseManagementDomainError):
    """Raised when domain object validation fails."""
    
    def __init__(self, field: str, message: str, details: Optional[dict[str, Any]] = None) -> None:
        full_message = f"Validation error for {field}: {message}"
        super().__init__(full_message, details)
        self.field = field