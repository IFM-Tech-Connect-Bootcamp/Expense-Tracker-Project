"""FirstName value object with validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class FirstName:
    """A validated first name value object.
    
    This value object ensures first names meet business requirements
    and provides type safety for name operations.
    """
    
    value: str
    
    def __post_init__(self) -> None:
        """Validate the first name."""
        if not isinstance(self.value, str):
            raise TypeError("First name must be a string")
        
        # Normalize the name (strip whitespace and title case)
        normalized = self.value.strip().title()
        object.__setattr__(self, 'value', normalized)
        
        if not normalized:
            raise ValueError("First name cannot be empty")
        
        if len(normalized) < 2:
            raise ValueError("First name must be at least 2 characters long")
        
        if len(normalized) > 50:
            raise ValueError("First name cannot exceed 50 characters")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(char.isalpha() or char in [' ', '-', "'"] for char in normalized):
            raise ValueError("First name can only contain letters, spaces, hyphens, and apostrophes")
    
    @classmethod
    def create(cls, value: str) -> Self:
        """Create a FirstName instance with explicit validation.
        
        Args:
            value: The first name string to validate.
            
        Returns:
            FirstName instance.
            
        Raises:
            ValueError: If the first name is invalid.
            TypeError: If value is not a string.
        """
        return cls(value)
    
    def __str__(self) -> str:
        """Return string representation of the first name."""
        return self.value
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"FirstName('{self.value}')"