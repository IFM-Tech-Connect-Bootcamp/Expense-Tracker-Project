"""CategoryName value object with validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Self


@dataclass(frozen=True, slots=True)
class CategoryName:
    """A value object representing a CategoryName for an expense.
    
    This class ensures that the CategoryName is a non-empty string with a maximum length of 255 characters.
    """
    
    value: str
    MAX_LENGTH: ClassVar[int] = 255
    CategoryName_REGEX: ClassVar[re.Pattern] = re.compile(r"^[\w\s.,'-]{1,255}$")
    
    
    
    def __post_init__(self) -> None:
        """Validate the CategoryName value."""
        if not isinstance(self.value, str):
            raise TypeError("CategoryName value must be a string")
        if not (1 <= len(self.value) <= self.MAX_LENGTH):
            raise ValueError(f"CategoryName value must be between 1 and {self.MAX_LENGTH} characters")
        if not self.CategoryName_REGEX.match(self.value):
            raise ValueError("CategoryName contains invalid characters")
    
    
    
    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create a CategoryName from a string representation.
        
        Args:
            value: String representation of the CategoryName.
            
        Returns:
            CategoryName instance.
            
        Raises:
            ValueError: If the string is not a valid CategoryName.
        """
        try:
            return cls(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid CategoryName string: {value}") from e