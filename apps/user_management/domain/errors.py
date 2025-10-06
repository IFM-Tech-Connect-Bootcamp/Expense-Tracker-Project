"""Domain-specific exceptions for User Management.

This module contains all the domain-level exceptions that can be raised
during user management operations. These exceptions represent business
rule violations and domain invariant failures.
"""

from typing import Any, Optional


class UserManagementDomainError(Exception):
    """Base exception for all user management domain errors.
    
    This is the base class for all domain-specific exceptions in the
    user management bounded context.
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





class UserAlreadyExistsError(UserManagementDomainError):
    """Raised when attempting to create a user that already exists.
    
    This typically occurs when trying to register with an email address
    that is already in use by another user.
    """
    
    def __init__(self, email: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"User with email '{email}' already exists"
        super().__init__(message, details)
        self.email = email






class UserNotFoundError(UserManagementDomainError):
    """Raised when a requested user cannot be found.
    
    This occurs when trying to perform operations on a user that
    doesn't exist in the system.
    """
    
    def __init__(self, identifier: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"User not found: {identifier}"
        super().__init__(message, details)
        self.identifier = identifier






class InvalidCredentialsError(UserManagementDomainError):
    """Raised when authentication fails due to invalid credentials.
    
    This occurs during login when the provided email/password combination
    is incorrect.
    """
    
    def __init__(self, email: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Invalid credentials for user: {email}"
        super().__init__(message, details)
        self.email = email






class InvalidOperationError(UserManagementDomainError):
    """Raised when attempting an operation that violates business rules.
    
    This occurs when trying to perform operations that are not allowed
    in the current context (e.g., updating a deactivated user).
    """
    
    def __init__(self, operation: str, reason: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Invalid operation '{operation}': {reason}"
        super().__init__(message, details)
        self.operation = operation
        self.reason = reason






class InvalidEmailError(UserManagementDomainError):
    """Raised when an email address is invalid.
    
    This occurs when email validation fails due to format issues.
    """
    
    def __init__(self, email: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Invalid email format: {email}"
        super().__init__(message, details)
        self.email = email






class PasswordPolicyError(UserManagementDomainError):
    """Raised when a password doesn't meet policy requirements.
    
    This occurs when password validation fails due to policy violations
    (length, complexity, etc.).
    """
    
    def __init__(self, policy_violation: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"Password policy violation: {policy_violation}"
        super().__init__(message, details)
        self.policy_violation = policy_violation







class UserDeactivatedError(UserManagementDomainError):
    """Raised when attempting operations on a deactivated user.
    
    This occurs when trying to authenticate or perform operations
    on a user account that has been deactivated.
    """
    
    def __init__(self, user_identifier: str, details: Optional[dict[str, Any]] = None) -> None:
        message = f"User is deactivated: {user_identifier}"
        super().__init__(message, details)
        self.user_identifier = user_identifier







class DomainValidationError(UserManagementDomainError):
    """Raised when domain entity validation fails.
    
    This is a general validation error for domain entity invariants.
    """
    
    def __init__(
        self, 
        entity_type: str, 
        validation_error: str, 
        details: Optional[dict[str, Any]] = None
    ) -> None:
        message = f"{entity_type} validation failed: {validation_error}"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.validation_error = validation_error