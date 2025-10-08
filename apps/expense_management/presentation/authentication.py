"""
Authentication middleware for Expense Management API endpoints.

This module provides authentication utilities that integrate with the
User Management context's JWT authentication system.
"""

from rest_framework.request import Request
from rest_framework.exceptions import AuthenticationFailed
from typing import Optional, Dict, Any
import logging

# Import User Management authentication
from apps.user_management.presentation.authentication import JWTAuthentication, UserProxy


logger = logging.getLogger(__name__)


def get_current_user_from_request(request: Request) -> str:
    """Extract the current user ID from the authenticated request.
    
    Args:
        request: Django REST Framework request object.
        
    Returns:
        User ID string from the authenticated user.
        
    Raises:
        AuthenticationFailed: If user is not authenticated or user ID cannot be extracted.
    """
    if not hasattr(request, 'user') or not request.user:
        logger.warning("Authentication required: No user found in request")
        raise AuthenticationFailed("Authentication required")
    
    if not request.user.is_authenticated:
        logger.warning("Authentication required: User not authenticated")
        raise AuthenticationFailed("Authentication required")
    
    # Extract user ID from UserProxy
    if isinstance(request.user, UserProxy):
        user_id = str(request.user.id)
        logger.debug(f"Extracted user ID from authenticated request: {user_id}")
        return user_id
    
    # Fallback for other user types
    if hasattr(request.user, 'id'):
        user_id = str(request.user.id)
        logger.debug(f"Extracted user ID from request.user.id: {user_id}")
        return user_id
    
    logger.error("Unable to extract user ID from authenticated request")
    raise AuthenticationFailed("Unable to extract user information")


def verify_expense_ownership(expense_user_id: str, request_user_id: str) -> None:
    """Verify that the expense belongs to the authenticated user.
    
    Args:
        expense_user_id: User ID associated with the expense.
        request_user_id: User ID from the authenticated request.
        
    Raises:
        AuthenticationFailed: If the expense doesn't belong to the authenticated user.
    """
    if expense_user_id != request_user_id:
        logger.warning(
            f"Access denied: User {request_user_id} attempted to access "
            f"expense belonging to user {expense_user_id}"
        )
        raise AuthenticationFailed("Access denied: You can only access your own expenses")


def verify_category_ownership(category_user_id: str, request_user_id: str) -> None:
    """Verify that the category belongs to the authenticated user.
    
    Args:
        category_user_id: User ID associated with the category.
        request_user_id: User ID from the authenticated request.
        
    Raises:
        AuthenticationFailed: If the category doesn't belong to the authenticated user.
    """
    if category_user_id != request_user_id:
        logger.warning(
            f"Access denied: User {request_user_id} attempted to access "
            f"category belonging to user {category_user_id}"
        )
        raise AuthenticationFailed("Access denied: You can only access your own categories")


# Re-export User Management authentication classes for consistency
__all__ = [
    'JWTAuthentication',
    'UserProxy',
    'get_current_user_from_request',
    'verify_expense_ownership',
    'verify_category_ownership',
]