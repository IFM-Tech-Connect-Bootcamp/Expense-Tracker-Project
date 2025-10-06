"""Service adapters for bridging infrastructure and application layers.

This module provides adapter classes that adapt infrastructure services
to match the interfaces expected by the application layer.
"""

from __future__ import annotations

from typing import Protocol

from ..domain.services.password_policy import PasswordHasher as DomainPasswordHasher
from ..domain.services.password_policy import PasswordPolicy as DomainPasswordPolicy
from ..domain.services.password_policy import TokenProvider as DomainTokenProvider
from ..domain.value_objects.password_hash import PasswordHash
from ..domain.value_objects.user_id import UserId
from .auth.bcrypt_hasher import BcryptPasswordHasher
from .auth.jwt_provider import JWTTokenProvider
from .auth.password_policy import DefaultPasswordPolicy


class PasswordService(Protocol):
    """Protocol for application layer password service."""
    
    async def hash_password(self, password: str) -> str:
        """Hash a password."""
        ...
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        ...


class InfrastructurePasswordService:
    """Adapter for infrastructure password services to application layer interface.
    
    This adapter bridges the domain PasswordHasher and PasswordPolicy
    to provide the async interface expected by application handlers.
    """
    
    def __init__(
        self,
        password_hasher: DomainPasswordHasher,
        password_policy: DomainPasswordPolicy,
    ) -> None:
        """Initialize the password service adapter.
        
        Args:
            password_hasher: Domain password hasher implementation.
            password_policy: Domain password policy implementation.
        """
        self._hasher = password_hasher
        self._policy = password_policy
    
    async def hash_password(self, password: str) -> str:
        """Hash a password asynchronously.
        
        Args:
            password: Plain text password to hash.
            
        Returns:
            Hashed password string.
            
        Raises:
            PasswordPolicyError: If password doesn't meet policy requirements.
        """
        # Validate password against policy first
        await self._policy.validate_password_strength(password)
        
        # Hash the password (domain services are async)
        password_hash = await self._hasher.hash(password)
        return password_hash.value
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash asynchronously.
        
        Args:
            password: Plain text password to verify.
            hashed: Hashed password to verify against.
            
        Returns:
            True if password matches hash, False otherwise.
        """
        password_hash = PasswordHash(hashed)
        return await self._hasher.verify(password_hash, password)


class InfrastructureTokenService:
    """Adapter for infrastructure token services to application layer interface.
    
    This adapter provides async token operations using the domain TokenProvider.
    """
    
    def __init__(self, token_provider: DomainTokenProvider) -> None:
        """Initialize the token service adapter.
        
        Args:
            token_provider: Domain token provider implementation.
        """
        self._provider = token_provider
    
    async def generate_token(self, user_id: str, claims: dict[str, str] | None = None) -> str:
        """Generate a JWT token asynchronously.
        
        Args:
            user_id: User ID to include in token.
            claims: Optional additional claims.
            
        Returns:
            JWT token string.
        """
        domain_user_id = UserId.from_string(user_id)
        return await self._provider.issue_token(domain_user_id, claims)
    
    async def verify_token(self, token: str) -> str:
        """Verify a JWT token and extract user ID asynchronously.
        
        Args:
            token: JWT token to verify.
            
        Returns:
            User ID string from token.
            
        Raises:
            ValueError: If token is invalid.
        """
        user_id = await self._provider.verify_token(token)
        return str(user_id)
    
    async def refresh_token(self, token: str) -> str:
        """Refresh a JWT token asynchronously.
        
        Args:
            token: Existing token to refresh.
            
        Returns:
            New JWT token string.
            
        Raises:
            ValueError: If token cannot be refreshed.
        """
        return await self._provider.refresh_token(token)


def create_password_service(
    hasher: BcryptPasswordHasher | None = None,
    policy: DefaultPasswordPolicy | None = None,
) -> PasswordService:
    """Factory function to create a password service with default implementations.
    
    Args:
        hasher: Optional password hasher (uses default if None).
        policy: Optional password policy (uses default if None).
        
    Returns:
        PasswordService implementation.
    """
    if hasher is None:
        hasher = BcryptPasswordHasher()
    
    if policy is None:
        policy = DefaultPasswordPolicy()
    
    return InfrastructurePasswordService(hasher, policy)


def create_token_service(provider: JWTTokenProvider | None = None) -> InfrastructureTokenService:
    """Factory function to create a token service with default implementation.
    
    Args:
        provider: Optional token provider (uses default if None).
        
    Returns:
        InfrastructureTokenService implementation.
    """
    if provider is None:
        provider = JWTTokenProvider()
    
    return InfrastructureTokenService(provider)