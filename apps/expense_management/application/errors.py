"""Application layer errors for Expense Management.

This module contains application-specific exceptions and error translation
utilities for the expense management bounded context.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from ..domain.errors import (
    ExpenseManagementDomainError,
    ExpenseNotFoundError as DomainExpenseNotFoundError,
    ExpenseAccessDeniedError as DomainExpenseAccessDeniedError,
    InvalidExpenseDataError as DomainInvalidExpenseDataError,
    CategoryNotFoundError as DomainCategoryNotFoundError,
    CategoryAccessDeniedError as DomainCategoryAccessDeniedError,
    DuplicateCategoryNameError as DomainDuplicateCategoryNameError,
    CategoryInUseError as DomainCategoryInUseError,
    InvalidCategoryDataError as DomainInvalidCategoryDataError,
    UserNotFoundError as DomainUserNotFoundError,
    BusinessRuleViolationError as DomainBusinessRuleViolationError,
    ValidationError as DomainValidationError,
)


class ApplicationError(Exception):
    """Base exception for application layer errors.
    
    All application layer exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """Initialize application error.
        
        Args:
            message: Human-readable error message.
            details: Optional additional error details.
            cause: Optional underlying exception that caused this error.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class ExpenseCreationFailedError(ApplicationError):
    """Raised when expense creation fails."""
    pass


class ExpenseUpdateFailedError(ApplicationError):
    """Raised when expense update fails."""
    pass


class ExpenseDeleteFailedError(ApplicationError):
    """Raised when expense deletion fails."""
    pass


class ExpenseNotFoundError(ApplicationError):
    """Raised when an expense cannot be found."""
    pass


class ExpenseAccessDeniedError(ApplicationError):
    """Raised when user tries to access expense they don't own."""
    pass


class CategoryCreationFailedError(ApplicationError):
    """Raised when category creation fails."""
    pass


class CategoryUpdateFailedError(ApplicationError):
    """Raised when category update fails."""
    pass


class CategoryDeleteFailedError(ApplicationError):
    """Raised when category deletion fails."""
    pass


class CategoryNotFoundError(ApplicationError):
    """Raised when a category cannot be found."""
    pass


class CategoryAccessDeniedError(ApplicationError):
    """Raised when user tries to access category they don't own."""
    pass


class DuplicateCategoryNameError(ApplicationError):
    """Raised when user tries to create category with duplicate name."""
    pass


class CategoryInUseError(ApplicationError):
    """Raised when user tries to delete category that has expenses."""
    pass


class ExpenseSummaryFailedError(ApplicationError):
    """Raised when expense summary generation fails."""
    pass


class UserNotFoundError(ApplicationError):
    """Raised when a user cannot be found."""
    pass


class ValidationError(ApplicationError):
    """Raised when input validation fails."""
    pass


class BusinessRuleViolationError(ApplicationError):
    """Raised when business rules are violated."""
    pass


def translate_domain_error(domain_error: ExpenseManagementDomainError) -> ApplicationError:
    """Translate domain errors to application errors.
    
    This function maps domain layer exceptions to appropriate
    application layer exceptions with enhanced context.
    
    Args:
        domain_error: The domain error to translate.
        
    Returns:
        Corresponding application error.
    """
    error_details = getattr(domain_error, 'details', {})
    
    # Expense-related errors
    if isinstance(domain_error, DomainExpenseNotFoundError):
        return ExpenseNotFoundError(
            message=f"Expense not found: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainExpenseAccessDeniedError):
        return ExpenseAccessDeniedError(
            message=f"Access denied to expense: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainInvalidExpenseDataError):
        return ValidationError(
            message=f"Invalid expense data: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    # Category-related errors
    if isinstance(domain_error, DomainCategoryNotFoundError):
        return CategoryNotFoundError(
            message=f"Category not found: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainCategoryAccessDeniedError):
        return CategoryAccessDeniedError(
            message=f"Access denied to category: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainDuplicateCategoryNameError):
        return DuplicateCategoryNameError(
            message=f"Category name already exists: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainCategoryInUseError):
        return CategoryInUseError(
            message=f"Category is in use and cannot be deleted: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainInvalidCategoryDataError):
        return ValidationError(
            message=f"Invalid category data: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    # General errors
    if isinstance(domain_error, DomainUserNotFoundError):
        return UserNotFoundError(
            message=f"User not found: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainBusinessRuleViolationError):
        return BusinessRuleViolationError(
            message=f"Business rule violation: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    if isinstance(domain_error, DomainValidationError):
        return ValidationError(
            message=f"Validation error: {domain_error}",
            details=error_details,
            cause=domain_error
        )
    
    # Fallback for unknown domain errors
    return ApplicationError(
        message=f"Unexpected domain error: {domain_error}",
        details=error_details,
        cause=domain_error
    )