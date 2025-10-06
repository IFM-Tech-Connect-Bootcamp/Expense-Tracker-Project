"""PasswordHash value object for secure password storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class PasswordHash:
    """A hashed password value object.
    
    This value object stores only the hashed representation of passwords,
    never the plain text. It provides type safety for password operations.
    """
    
    value: str
    
    def __post_init__(self) -> None:
        """Validate the password hash."""
        if not isinstance(self.value, str):
            raise TypeError("Password hash must be a string")
        
        if not self.value.strip():
            raise ValueError("Password hash cannot be empty")
        
        # Basic validation - hash should be non-empty and reasonable length
        if len(self.value.strip()) < 10:
            raise ValueError("Password hash appears to be invalid (too short)")
    
    
    
    
    @classmethod
    def create(cls, hash_value: str) -> Self:
        """Create a PasswordHash instance.
        
        Args:
            hash_value: The hashed password string.
            
        Returns:
            PasswordHash instance.
            
        Raises:
            ValueError: If the hash is invalid.
            TypeError: If hash_value is not a string.
        """
        return cls(hash_value.strip())
    
    
    
    
    def __str__(self) -> str:
        """Return a masked representation for security."""
        return "***MASKED***"
    
    
    
    
    def __repr__(self) -> str:
        """Return a masked representation for security."""
        return "PasswordHash(***MASKED***)"
    
    
    
    
    def reveal(self) -> str:
        """Reveal the actual hash value.
        
        This method should only be used when the hash needs to be
        passed to password verification functions.
        
        Returns:
            The actual hash string.
        """
        return self.value