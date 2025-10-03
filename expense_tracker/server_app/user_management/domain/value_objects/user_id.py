"""UserId value object for user identification."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class UserId:
    """A unique identifier for a user.
    
    This value object wraps a UUID to provide type safety and domain meaning.
    """
    
    value: uuid.UUID
    
    
    
    
    def __post_init__(self) -> None:
        """Validate the UUID value."""
        if not isinstance(self.value, uuid.UUID):
            raise TypeError("UserId value must be a UUID instance")
    
    
    
    
    @classmethod
    def new(cls) -> Self:
        """Generate a new unique UserId.
        
        Returns:
            A new UserId with a randomly generated UUID.
        """
        return cls(uuid.uuid4())
    
    
    
    
    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create a UserId from a string representation.
        
        Args:
            value: String representation of a UUID.
            
        Returns:
            UserId instance.
            
        Raises:
            ValueError: If the string is not a valid UUID.
        """
        try:
            return cls(uuid.UUID(value))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid UUID string: {value}") from e
    
    
    
    
    def __str__(self) -> str:
        """Return string representation of the UserId."""
        return str(self.value)
    
    
    
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"UserId({self.value!r})"