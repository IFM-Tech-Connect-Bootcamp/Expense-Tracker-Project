"""Bcrypt password hasher implementation.

This module provides a concrete implementation of the PasswordHasher
domain service using bcrypt for secure password hashing.
"""

from __future__ import annotations

import logging
from typing import Protocol

from passlib.hash import bcrypt

from ...domain.services.password_policy import PasswordHasher
from ...domain.value_objects.password_hash import PasswordHash

logger = logging.getLogger(__name__)


class BcryptPasswordHasher(PasswordHasher):
    """Bcrypt implementation of PasswordHasher domain service.
    
    Uses passlib's bcrypt implementation for secure password hashing.
    Provides configurable rounds for computational cost adjustment.
    """

    def __init__(self, rounds: int = 12) -> None:
        """Initialize bcrypt password hasher.
        
        Args:
            rounds: Number of bcrypt rounds (computational cost).
                   Higher values are more secure but slower.
                   Default: 12 (recommended for 2025).
        """
        if rounds < 4 or rounds > 31:
            raise ValueError("Bcrypt rounds must be between 4 and 31")
        
        self._rounds = rounds
        self._hasher = bcrypt.using(rounds=rounds)
        logger.debug(f"Initialized BcryptPasswordHasher with {rounds} rounds")

    def hash_password(self, password: str) -> str:
        """Hash a plain text password using bcrypt.
        
        Args:
            password: Plain text password to hash.
            
        Returns:
            Bcrypt hash string.
            
        Raises:
            ValueError: If password is empty or hashing fails.
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        logger.debug("Hashing password with bcrypt")
        
        try:
            # Use passlib's bcrypt implementation
            hashed = self._hasher.hash(password)
            logger.debug("Successfully hashed password")
            return hashed
        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise ValueError(f"Password hashing failed: {e}") from e

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            password: Plain text password to verify.
            hashed: Bcrypt hash to verify against.
            
        Returns:
            True if password matches hash, False otherwise.
            
        Raises:
            ValueError: If verification fails due to invalid input.
        """
        if not password:
            logger.debug("Password verification failed: empty password")
            return False
        
        if not hashed:
            logger.debug("Password verification failed: empty hash")
            return False
        
        logger.debug("Verifying password against bcrypt hash")
        
        try:
            # Use passlib's bcrypt verification
            is_valid = bcrypt.verify(password, hashed)
            logger.debug(f"Password verification result: {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            # Don't raise exception for verification errors - return False
            return False

    def needs_rehash(self, hashed: str) -> bool:
        """Check if password hash needs rehashing.
        
        Useful for upgrading hash parameters over time.
        
        Args:
            hashed: Existing password hash.
            
        Returns:
            True if hash should be upgraded, False otherwise.
        """
        if not hashed:
            return True
        
        try:
            # Check if hash uses current rounds setting
            needs_upgrade = not bcrypt.verify("dummy", hashed, rounds=self._rounds)
            logger.debug(f"Hash needs rehash: {needs_upgrade}")
            return needs_upgrade
        except Exception:
            # If we can't verify, assume it needs rehashing
            logger.debug("Hash verification failed, assuming rehash needed")
            return True

    @property
    def rounds(self) -> int:
        """Get current bcrypt rounds setting."""
        return self._rounds

    # Domain interface methods
    def hash(self, plain_password: str) -> PasswordHash:
        """Hash a plain text password (domain interface).
        
        Args:
            plain_password: Plain text password to hash.
            
        Returns:
            PasswordHash value object.
            
        Raises:
            ValueError: If password is empty or hashing fails.
        """
        hashed_str = self.hash_password(plain_password)
        return PasswordHash(hashed_str)

    def verify(self, password_hash: PasswordHash, plain_password: str) -> bool:
        """Verify a password against hash (domain interface).
        
        Args:
            password_hash: PasswordHash value object.
            plain_password: Plain text password to verify.
            
        Returns:
            True if password matches hash, False otherwise.
        """
        return self.verify_password(plain_password, password_hash.value)


class PasswordService:
    """Synchronous password service for password operations.
    
    Provides the PasswordService protocol implementation
    used by application layer handlers.
    """

    def __init__(self, hasher: BcryptPasswordHasher | None = None) -> None:
        """Initialize password service.
        
        Args:
            hasher: Optional password hasher. If None, creates default.
        """
        self._hasher = hasher or BcryptPasswordHasher()

    def hash_password(self, password: str) -> str:
        """Hash a password synchronously.
        
        Args:
            password: Plain text password.
            
        Returns:
            Hashed password string.
        """
        return self._hasher.hash_password(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password synchronously.
        
        Args:
            password: Plain text password.
            hashed: Password hash.
            
        Returns:
            True if password is valid, False otherwise.
        """
        return self._hasher.verify_password(password, hashed)

    def needs_rehash(self, hashed: str) -> bool:
        """Check if hash needs upgrading.
        
        Args:
            hashed: Password hash to check.
            
        Returns:
            True if hash should be upgraded.
        """
        return self._hasher.needs_rehash(hashed)


# Factory function for dependency injection
def create_password_service(rounds: int = 12) -> PasswordService:
    """Create a password service with specified bcrypt rounds.
    
    Args:
        rounds: Bcrypt rounds for computational cost.
        
    Returns:
        Configured password service instance.
    """
    hasher = BcryptPasswordHasher(rounds=rounds)
    return PasswordService(hasher)