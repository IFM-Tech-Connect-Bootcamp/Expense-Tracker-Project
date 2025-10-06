"""CategoryName value object for category names.

This module contains the CategoryName value object for category names.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class CategoryName:
    """A validated category name value object.
    
    This value object ensures category names are properly validated
    and provides type safety for category name operations.
    """
    
    value: str
    
    def __post_init__(self) -> None:
        """Validate the category name after initialization."""
        if not isinstance(self.value, str):
            raise TypeError("Category name value must be a string")
        
        # Normalize the category name (strip whitespace)
        normalized = self.value.strip()
        
        if not normalized:
            raise ValueError("Category name cannot be empty")
        
        if len(normalized) > 100:
            raise ValueError("Category name cannot exceed 100 characters")
        
        # Set the normalized value
        object.__setattr__(self, 'value', normalized)
    
    @classmethod
    def from_string(cls, name: str) -> Self:
        """Create CategoryName from string.
        
        Args:
            name: Category name string.
            
        Returns:
            CategoryName instance.
            
        Raises:
            ValueError: If name is invalid.
            TypeError: If name is not a string.
        """
        return cls(value=name)
    
    def __str__(self) -> str:
        """Return string representation of the category name."""
        return self.value
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"CategoryName({self.value!r})"