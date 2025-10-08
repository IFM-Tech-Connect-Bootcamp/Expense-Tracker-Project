"""
Shared response standards for all API endpoints.

This module defines consistent response formats, error codes, and
success patterns that should be used across all bounded contexts
in the expense tracker application.
"""

from typing import Dict, Any, Optional, List, Union
from enum import Enum


class ResponseStatus(str, Enum):
    """Standard response status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class StandardErrorCodes(str, Enum):
    """Standardized error codes used across all contexts."""
    
    # Generic errors (1xxx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Authentication & Authorization errors (2xxx)
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    ACCESS_DENIED = "ACCESS_DENIED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # User Management errors (3xxx)
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_DEACTIVATED = "USER_DEACTIVATED"
    PASSWORD_POLICY_VIOLATION = "PASSWORD_POLICY_VIOLATION"
    EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"
    INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
    REGISTRATION_FAILED = "REGISTRATION_FAILED"
    PROFILE_UPDATE_FAILED = "PROFILE_UPDATE_FAILED"
    PASSWORD_CHANGE_FAILED = "PASSWORD_CHANGE_FAILED"
    USER_DEACTIVATION_FAILED = "USER_DEACTIVATION_FAILED"
    
    # Expense Management errors (4xxx)
    EXPENSE_NOT_FOUND = "EXPENSE_NOT_FOUND"
    EXPENSE_ACCESS_DENIED = "EXPENSE_ACCESS_DENIED"
    EXPENSE_CREATION_FAILED = "EXPENSE_CREATION_FAILED"
    EXPENSE_UPDATE_FAILED = "EXPENSE_UPDATE_FAILED"
    EXPENSE_DELETION_FAILED = "EXPENSE_DELETION_FAILED"
    INVALID_EXPENSE_DATA = "INVALID_EXPENSE_DATA"
    
    # Category Management errors (5xxx)
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    CATEGORY_ACCESS_DENIED = "CATEGORY_ACCESS_DENIED"
    DUPLICATE_CATEGORY_NAME = "DUPLICATE_CATEGORY_NAME"
    CATEGORY_IN_USE = "CATEGORY_IN_USE"
    CATEGORY_CREATION_FAILED = "CATEGORY_CREATION_FAILED"
    CATEGORY_UPDATE_FAILED = "CATEGORY_UPDATE_FAILED"
    CATEGORY_DELETION_FAILED = "CATEGORY_DELETION_FAILED"
    INVALID_CATEGORY_DATA = "INVALID_CATEGORY_DATA"
    
    # Business Logic errors (6xxx)
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    PRECONDITION_FAILED = "PRECONDITION_FAILED"


class StandardHttpMessages:
    """Standard HTTP response messages."""
    
    # Success messages
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    RETRIEVED = "Resource retrieved successfully"
    OPERATION_COMPLETED = "Operation completed successfully"
    
    # Error messages
    NOT_FOUND = "The requested resource was not found"
    UNAUTHORIZED = "Authentication credentials were not provided or are invalid"
    FORBIDDEN = "You do not have permission to perform this action"
    BAD_REQUEST = "The request contains invalid data"
    CONFLICT = "The request conflicts with the current state of the resource"
    INTERNAL_ERROR = "An internal server error occurred"
    SERVICE_UNAVAILABLE = "The service is temporarily unavailable"


class StandardResponseBuilder:
    """Builder for creating standardized API responses."""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = StandardHttpMessages.OPERATION_COMPLETED,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a success response.
        
        Args:
            data: The response payload
            message: Success message
            meta: Additional metadata (pagination, counts, etc.)
            
        Returns:
            Standardized success response dictionary
        """
        response = {
            "status": ResponseStatus.SUCCESS,
            "message": message,
        }
        
        if data is not None:
            response["data"] = data
            
        if meta:
            response["meta"] = meta
            
        return response
    
    @staticmethod
    def error(
        message: str,
        code: str = StandardErrorCodes.INTERNAL_ERROR,
        details: Optional[Union[Dict[str, Any], List[str]]] = None,
        field_errors: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """Build an error response.
        
        Args:
            message: Human-readable error message
            code: Machine-readable error code
            details: Additional error details
            field_errors: Field-specific validation errors
            
        Returns:
            Standardized error response dictionary
        """
        response = {
            "status": ResponseStatus.ERROR,
            "message": message,
            "code": code,
        }
        
        if details:
            response["details"] = details
            
        if field_errors:
            response["field_errors"] = field_errors
            
        return response
    
    @staticmethod
    def created(
        data: Any,
        message: str = StandardHttpMessages.CREATED,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a resource creation success response.
        
        Args:
            data: The created resource data
            message: Success message
            location: Location header value for the created resource
            
        Returns:
            Standardized creation response dictionary
        """
        response = StandardResponseBuilder.success(data, message)
        
        if location:
            response["location"] = location
            
        return response
    
    @staticmethod
    def updated(
        data: Any,
        message: str = StandardHttpMessages.UPDATED
    ) -> Dict[str, Any]:
        """Build a resource update success response.
        
        Args:
            data: The updated resource data
            message: Success message
            
        Returns:
            Standardized update response dictionary
        """
        return StandardResponseBuilder.success(data, message)
    
    @staticmethod
    def deleted(
        message: str = StandardHttpMessages.DELETED,
        data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Build a resource deletion success response.
        
        Args:
            message: Success message
            data: Optional data about the deleted resource
            
        Returns:
            Standardized deletion response dictionary
        """
        return StandardResponseBuilder.success(data, message)
    
    @staticmethod
    def list_response(
        items: List[Any],
        total_count: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        message: str = StandardHttpMessages.RETRIEVED
    ) -> Dict[str, Any]:
        """Build a list/collection response with pagination metadata.
        
        Args:
            items: List of items
            total_count: Total number of items available
            page: Current page number
            page_size: Number of items per page
            message: Success message
            
        Returns:
            Standardized list response dictionary
        """
        meta = {}
        
        if total_count is not None:
            meta["total_count"] = total_count
            
        if page is not None:
            meta["page"] = page
            
        if page_size is not None:
            meta["page_size"] = page_size
            meta["has_more"] = len(items) == page_size
            
        return StandardResponseBuilder.success(
            data=items,
            message=message,
            meta=meta if meta else None
        )
    
    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, List[str]]] = None,
        general_errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build a validation error response.
        
        Args:
            message: General validation error message
            field_errors: Field-specific validation errors
            general_errors: General validation errors
            
        Returns:
            Standardized validation error response dictionary
        """
        details = {}
        
        if general_errors:
            details["general"] = general_errors
            
        return StandardResponseBuilder.error(
            message=message,
            code=StandardErrorCodes.VALIDATION_ERROR,
            details=details if details else None,
            field_errors=field_errors
        )


class HealthCheckResponse:
    """Standard health check response format."""
    
    @staticmethod
    def healthy(
        service_name: str,
        version: str = "1.0.0",
        dependencies: Optional[Dict[str, str]] = None,
        handlers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build a healthy service response.
        
        Args:
            service_name: Name of the service
            version: Service version
            dependencies: Status of service dependencies
            handlers: List of available handlers/operations
            
        Returns:
            Standard health check response
        """
        response = {
            "status": "healthy",
            "service": service_name,
            "version": version,
            "timestamp": None,  # Will be set by the view
        }
        
        if dependencies:
            response["dependencies"] = dependencies
            
        if handlers:
            response["handlers_available"] = handlers
            
        return response
    
    @staticmethod
    def unhealthy(
        service_name: str,
        errors: List[str],
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """Build an unhealthy service response.
        
        Args:
            service_name: Name of the service
            errors: List of health check errors
            version: Service version
            
        Returns:
            Standard unhealthy response
        """
        return {
            "status": "unhealthy",
            "service": service_name,
            "version": version,
            "errors": errors,
            "timestamp": None,  # Will be set by the view
        }


# Common response messages for specific operations
class CommonMessages:
    """Common messages for specific operations."""
    
    # User Management
    USER_REGISTERED = "User account created successfully"
    USER_AUTHENTICATED = "User authenticated successfully"
    USER_PROFILE_RETRIEVED = "User profile retrieved successfully"
    USER_PROFILE_UPDATED = "User profile updated successfully"
    PASSWORD_CHANGED = "Password changed successfully"
    USER_DEACTIVATED = "User account deactivated successfully"
    
    # Expense Management
    EXPENSE_CREATED = "Expense created successfully"
    EXPENSE_UPDATED = "Expense updated successfully"
    EXPENSE_DELETED = "Expense deleted successfully"
    EXPENSE_RETRIEVED = "Expense retrieved successfully"
    EXPENSES_LISTED = "Expenses retrieved successfully"
    EXPENSE_SUMMARY_RETRIEVED = "Expense summary retrieved successfully"
    
    # Category Management
    CATEGORY_CREATED = "Category created successfully"
    CATEGORY_UPDATED = "Category updated successfully"
    CATEGORY_DELETED = "Category deleted successfully"
    CATEGORY_RETRIEVED = "Category retrieved successfully"
    CATEGORIES_LISTED = "Categories retrieved successfully"