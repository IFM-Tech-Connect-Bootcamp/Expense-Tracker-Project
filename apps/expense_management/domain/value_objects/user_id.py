"""UserId value object for user identification in expense management.

This module contains the UserId value object for user identification.
Note: This is a shared value object that represents the User from 
the UserManagement bounded context within ExpenseManagement.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class UserId:
    """A unique identifier for a user in expense management context.
    
    This value object wraps a UUID to provide type safety and domain meaning.
    It represents users from the UserManagement bounded context.
    """
    
    value: uuid.UUID
    
    def __post_init__(self) -> None:
        """Validate the UUID value."""
        if not isinstance(self.value, uuid.UUID):
            raise TypeError("UserId value must be a UUID instance")
    
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