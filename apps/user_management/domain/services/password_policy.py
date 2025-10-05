"""Password policy domain service interface.

This module defines the interface for password policy validation
and password hashing operations required by the domain.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from ..value_objects.password_hash import PasswordHash
from ..value_objects.user_id import UserId


class PasswordPolicy(Protocol):
    """Interface for password policy validation.
    
    This protocol defines the contract for validating passwords
    against domain-specific business rules and policies.
    """
    
    async def validate_password_strength(self, password: str) -> None:
        """Validate that a password meets strength requirements.
        
        Args:
            password: The plain text password to validate.
            
        Raises:
            PasswordPolicyError: If the password doesn't meet requirements.
        """
        ...





class PasswordHasher(Protocol):
    """Interface for password hashing operations.
    
    This protocol defines the contract for hashing and verifying passwords.
    The implementation should use a secure hashing algorithm like bcrypt.
    """
    
    async def hash(self, plain_password: str) -> PasswordHash:
        """Hash a plain text password.
        
        Args:
            plain_password: The plain text password to hash.
            
        Returns:
            A PasswordHash value object containing the hashed password.
            
        Raises:
            ValueError: If the password is invalid.
        """
        ...
    
    async def verify(self, password_hash: PasswordHash, plain_password: str) -> bool:
        """Verify a plain text password against a hash.
        
        Args:
            password_hash: The stored password hash to verify against.
            plain_password: The plain text password to verify.
            
        Returns:
            True if the password matches the hash, False otherwise.
        """
        ...






class TokenProvider(Protocol):
    """Interface for JWT token operations.
    
    This protocol defines the contract for issuing and verifying
    authentication tokens used for user sessions.
    """
    
    async def issue_token(self, user_id: UserId, claims: dict[str, str] | None = None) -> str:
        """Issue a JWT token for a user.
        
        Args:
            user_id: The user ID to include in the token.
            claims: Optional additional claims to include in the token.
            
        Returns:
            A JWT token string.
            
        Raises:
            ValueError: If the user_id is invalid.
        """
        ...
    
    async def verify_token(self, token: str) -> UserId:
        """Verify a JWT token and extract the user ID.
        
        Args:
            token: The JWT token string to verify.
            
        Returns:
            The user ID from the token.
            
        Raises:
            ValueError: If the token is invalid or expired.
        """
        ...
    
    async def refresh_token(self, token: str) -> str:
        """Refresh an existing JWT token.
        
        Args:
            token: The existing JWT token to refresh.
            
        Returns:
            A new JWT token string.
            
        Raises:
            ValueError: If the token is invalid or cannot be refreshed.
        """
        ...






class UserDomainService(ABC):
    """Abstract base class for user domain services.
    
    This class provides common functionality that might be needed
    by domain services operating on user entities.
    """
    
    def __init__(self, password_hasher: PasswordHasher, password_policy: PasswordPolicy) -> None:
        """Initialize the domain service.
        
        Args:
            password_hasher: Password hashing service.
            password_policy: Password policy validation service.
        """
        self._password_hasher = password_hasher
        self._password_policy = password_policy
    
    @abstractmethod
    async def validate_business_rules(self, *args, **kwargs) -> None:
        """Validate domain-specific business rules.
        
        This method should be implemented by concrete domain services
        to validate business rules specific to their operations.
        """
        pass
    
    async def _validate_password(self, password: str) -> None:
        """Validate a password against domain policies.
        
        Args:
            password: The plain text password to validate.
            
        Raises:
            PasswordPolicyError: If the password violates policy.
        """
        await self._password_policy.validate_password_strength(password)