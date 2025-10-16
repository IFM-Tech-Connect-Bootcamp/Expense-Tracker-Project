"""Application-level exceptions for Expense Management.

This module contains application-specific exceptions that translate
domain errors and provide appropriate error handling for the application layer.
"""

from typing import Any, Dict, Optional


class ApplicationError(Exception):
    """Base exception for all application-level errors.
    
    This is the base class for all application-specific exceptions
    in the expense management application layer.
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """Initialize the application error.
        
        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional error details.
            cause: Optional underlying exception that caused this error.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause


class ValidationError(ApplicationError):
    """Raised when input validation fails.
    
    This error is raised when command or input validation fails
    before reaching the domain layer.
    """
    
    def __init__(
        self, 
        field: str,
        reason: str, 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"Validation failed for {field}: {reason}"
        super().__init__(message, details, cause)
        self.field = field
        self.reason = reason


class ExpenseNotFoundError(ApplicationError):
    """Raised when an expense cannot be found."""
    
    def __init__(
        self,
        expense_id: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"Expense not found: {expense_id}"
        super().__init__(message, details, cause)
        self.expense_id = expense_id


class CategoryNotFoundError(ApplicationError):
    """Raised when a category cannot be found."""
    
    def __init__(
        self,
        category_id: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"Category not found: {category_id}"
        super().__init__(message, details, cause)
        self.category_id = category_id


class UnauthorizedOperationError(ApplicationError):
    """Raised when attempting to access or modify an unauthorized resource."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"User {user_id} is not authorized to access {resource_type} {resource_id}"
        super().__init__(message, details, cause)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id