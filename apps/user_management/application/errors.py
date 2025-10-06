"""Application-level exceptions for User Management.

This module contains application-specific exceptions that translate
domain errors and provide appropriate error handling for the application layer.
"""

from typing import Any, Dict, Optional

from ..domain.errors import (
    UserManagementDomainError,
    UserAlreadyExistsError as DomainUserAlreadyExistsError,
    UserNotFoundError as DomainUserNotFoundError,
    InvalidCredentialsError as DomainInvalidCredentialsError,
    InvalidOperationError as DomainInvalidOperationError,
    UserDeactivatedError as DomainUserDeactivatedError
)


class ApplicationError(Exception):
    """Base exception for all application-level errors.
    
    This is the base class for all application-specific exceptions
    in the user management application layer.
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


class RegistrationFailedError(ApplicationError):
    """Raised when user registration fails.
    
    This error is raised when the registration process fails due to
    business rule violations or system constraints.
    """
    
    def __init__(
        self, 
        reason: str, 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"User registration failed: {reason}"
        super().__init__(message, details, cause)
        self.reason = reason


class AuthenticationFailedError(ApplicationError):
    """Raised when user authentication fails.
    
    This error is raised when login attempts fail due to invalid
    credentials or account status issues.
    """
    
    def __init__(
        self, 
        reason: str = "Invalid credentials", 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"Authentication failed: {reason}"
        super().__init__(message, details, cause)
        self.reason = reason


class ProfileUpdateFailedError(ApplicationError):
    """Raised when profile update operations fail.
    
    This error is raised when profile update attempts fail due to
    validation errors or business rule violations.
    """
    
    def __init__(
        self, 
        reason: str, 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"Profile update failed: {reason}"
        super().__init__(message, details, cause)
        self.reason = reason


class PasswordChangeFailedError(ApplicationError):
    """Raised when password change operations fail.
    
    This error is raised when password change attempts fail due to
    validation errors or business rule violations.
    """
    
    def __init__(
        self, 
        reason: str, 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"Password change failed: {reason}"
        super().__init__(message, details, cause)
        self.reason = reason


class UserDeactivationFailedError(ApplicationError):
    """Raised when user deactivation operations fail.
    
    This error is raised when deactivation attempts fail due to
    business rule violations or system constraints.
    """
    
    def __init__(
        self, 
        reason: str, 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"User deactivation failed: {reason}"
        super().__init__(message, details, cause)
        self.reason = reason


class UserNotFoundError(ApplicationError):
    """Raised when a requested user cannot be found.
    
    This is the application-level version of the domain UserNotFoundError.
    """
    
    def __init__(
        self, 
        identifier: str, 
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        message = f"User not found: {identifier}"
        super().__init__(message, details, cause)
        self.identifier = identifier


def translate_domain_error(domain_error: UserManagementDomainError) -> ApplicationError:
    """Translate domain errors to application errors.
    
    This function maps domain-level exceptions to appropriate
    application-level exceptions for better error handling.
    
    Args:
        domain_error: The domain error to translate.
        
    Returns:
        Appropriate application error.
    """
    if isinstance(domain_error, DomainUserAlreadyExistsError):
        return RegistrationFailedError(
            reason="Email address is already registered",
            details={'email': domain_error.email},
            cause=domain_error
        )
    
    elif isinstance(domain_error, DomainUserNotFoundError):
        return UserNotFoundError(
            identifier=domain_error.identifier,
            cause=domain_error
        )
    
    elif isinstance(domain_error, DomainInvalidCredentialsError):
        return AuthenticationFailedError(
            reason="Invalid email or password",
            details={'email': domain_error.email},
            cause=domain_error
        )
    
    elif isinstance(domain_error, DomainUserDeactivatedError):
        return AuthenticationFailedError(
            reason="Account is deactivated",
            details={'user_identifier': domain_error.user_identifier},
            cause=domain_error
        )
    
    elif isinstance(domain_error, DomainInvalidOperationError):
        # Map to appropriate application error based on operation
        operation = domain_error.operation
        
        if operation in ['update_profile']:
            return ProfileUpdateFailedError(
                reason=domain_error.reason,
                cause=domain_error
            )
        elif operation in ['change_password']:
            return PasswordChangeFailedError(
                reason=domain_error.reason,
                cause=domain_error
            )
        elif operation in ['deactivate']:
            return UserDeactivationFailedError(
                reason=domain_error.reason,
                cause=domain_error
            )
        else:
            return ApplicationError(
                message=domain_error.message,
                details=domain_error.details,
                cause=domain_error
            )
    
    else:
        # Generic mapping for unknown domain errors
        return ApplicationError(
            message=domain_error.message,
            details=getattr(domain_error, 'details', {}),
            cause=domain_error
        )