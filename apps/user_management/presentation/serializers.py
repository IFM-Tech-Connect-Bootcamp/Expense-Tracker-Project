"""
Serializers for User Management API endpoints.

This module contains Django REST Framework serializers that handle
request/response serialization for the user management presentation layer.
All serializers follow clean architecture principles by depending only
on DTOs and not directly on domain entities.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from typing import Dict, Any


class RegisterUserSerializer(serializers.Serializer):
    """Serializer for user registration requests."""
    
    email = serializers.EmailField(
        max_length=254,
        help_text="User's email address (must be unique)"
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'},
        help_text="User's password (minimum 8 characters)"
    )
    first_name = serializers.CharField(
        max_length=50,
        min_length=2,
        help_text="User's first name (2-50 characters)"
    )
    last_name = serializers.CharField(
        max_length=50,
        min_length=2,
        help_text="User's last name (2-50 characters)"
    )

    def validate_email(self, value: str) -> str:
        """Validate email format and normalization."""
        return value.lower().strip()

    def validate_first_name(self, value: str) -> str:
        """Validate and normalize first name."""
        name = value.strip()
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes")
        return name.title()

    def validate_last_name(self, value: str) -> str:
        """Validate and normalize last name."""
        name = value.strip()
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes")
        return name.title()


class AuthenticateUserSerializer(serializers.Serializer):
    """Serializer for user authentication requests."""
    
    email = serializers.EmailField(
        max_length=254,
        help_text="User's email address"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="User's password"
    )

    def validate_email(self, value: str) -> str:
        """Normalize email for authentication."""
        return value.lower().strip()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change requests."""
    
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Current password for verification"
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'},
        help_text="New password (minimum 8 characters)"
    )


class UpdateProfileSerializer(serializers.Serializer):
    """Serializer for profile update requests."""
    
    email = serializers.EmailField(
        max_length=254,
        required=False,
        help_text="New email address (optional)"
    )
    first_name = serializers.CharField(
        max_length=50,
        min_length=2,
        required=False,
        help_text="New first name (optional, 2-50 characters)"
    )
    last_name = serializers.CharField(
        max_length=50,
        min_length=2,
        required=False,
        help_text="New last name (optional, 2-50 characters)"
    )

    def validate_email(self, value: str) -> str:
        """Validate and normalize email."""
        return value.lower().strip()

    def validate_first_name(self, value: str) -> str:
        """Validate and normalize first name."""
        name = value.strip()
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes")
        return name.title()

    def validate_last_name(self, value: str) -> str:
        """Validate and normalize last name."""
        name = value.strip()
        if not name.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes")
        return name.title()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure at least one field is provided for update."""
        if not any(attrs.values()):
            raise ValidationError("At least one field must be provided for update")
        return attrs


class DeactivateUserSerializer(serializers.Serializer):
    """Serializer for user deactivation requests."""
    
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Reason for account deactivation (optional)"
    )


class UserResponseSerializer(serializers.Serializer):
    """Serializer for user data responses."""
    
    id = serializers.UUIDField(
        read_only=True,
        help_text="Unique user identifier"
    )
    email = serializers.EmailField(
        read_only=True,
        help_text="User's email address"
    )
    first_name = serializers.CharField(
        read_only=True,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        read_only=True,
        help_text="User's last name"
    )
    full_name = serializers.CharField(
        read_only=True,
        help_text="User's full name (first + last)"
    )
    status = serializers.CharField(
        read_only=True,
        help_text="User account status"
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="Account creation timestamp"
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text="Last update timestamp"
    )


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication response."""
    
    user = UserResponseSerializer(
        read_only=True,
        help_text="User information"
    )
    access_token = serializers.CharField(
        read_only=True,
        help_text="JWT access token"
    )
    token_type = serializers.CharField(
        read_only=True,
        default="Bearer",
        help_text="Token type (always Bearer)"
    )
    expires_in = serializers.IntegerField(
        read_only=True,
        help_text="Token expiration time in seconds"
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    
    error = serializers.CharField(
        read_only=True,
        help_text="Error message"
    )
    code = serializers.CharField(
        read_only=True,
        help_text="Error code"
    )
    details = serializers.DictField(
        read_only=True,
        required=False,
        help_text="Additional error details"
    )


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for success responses."""
    
    message = serializers.CharField(
        read_only=True,
        help_text="Success message"
    )
    data = serializers.DictField(
        read_only=True,
        required=False,
        help_text="Additional response data"
    )