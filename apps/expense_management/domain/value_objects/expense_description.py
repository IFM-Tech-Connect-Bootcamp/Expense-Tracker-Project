"""ExpenseDescription value object for expense descriptions.

This module contains the ExpenseDescription value object for expense descriptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Self


@dataclass(frozen=True, slots=True)
class ExpenseDescription:
    """A validated expense description value object.
    
    This value object ensures expense descriptions are properly validated
    and provides type safety for description operations.
    """
    
    value: Optional[str]
    
    def __post_init__(self) -> None:
        """Validate the description after initialization."""
        if self.value is not None:
            if not isinstance(self.value, str):
                raise TypeError("Description value must be a string or None")
            
            # Normalize the description (strip whitespace)
            normalized = self.value.strip()
            
            if len(normalized) == 0:
                # Convert empty string to None
                object.__setattr__(self, 'value', None)
            else:
                if len(normalized) > 500:
                    raise ValueError("Description cannot exceed 500 characters")
                object.__setattr__(self, 'value', normalized)
    
    @classmethod
    def from_string(cls, description: Optional[str]) -> Self:
        """Create ExpenseDescription from string.
        
        Args:
            description: Optional description string.
            
        Returns:
            ExpenseDescription instance.
        """
        return cls(value=description)
    
    @classmethod
    def empty(cls) -> Self:
        """Create an empty description.
        
        Returns:
            ExpenseDescription with None value.
        """
        return cls(value=None)
    
    def is_empty(self) -> bool:
        """Check if description is empty.
        
        Returns:
            True if description is None or empty, False otherwise.
        """
        return self.value is None
    
    def __str__(self) -> str:
        """Return string representation of the description."""
        return self.value or ""
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"ExpenseDescription({self.value!r})"
    
    def __bool__(self) -> bool:
        """Return True if description has content, False if empty."""
        return self.value is not None