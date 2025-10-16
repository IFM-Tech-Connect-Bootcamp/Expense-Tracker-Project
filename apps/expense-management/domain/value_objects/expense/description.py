"""Description value object with validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Self


@dataclass(frozen=True, slots=True)
class Description:
    """A value object representing a description for an expense.
    
    This class ensures that the description is a non-empty string with a maximum length of 255 characters.
    """
    
    value: str
    MAX_LENGTH: ClassVar[int] = 255
    DESCRIPTION_REGEX: ClassVar[re.Pattern] = re.compile(r"^[\w\s.,'-]{1,255}$")
    
    
    
    def __post_init__(self) -> None:
        """Validate the description value."""
        if not isinstance(self.value, str):
            raise TypeError("Description value must be a string")
        if not (1 <= len(self.value) <= self.MAX_LENGTH):
            raise ValueError(f"Description value must be between 1 and {self.MAX_LENGTH} characters")
        if not self.DESCRIPTION_REGEX.match(self.value):
            raise ValueError("Description contains invalid characters")
    
    
    
    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create a Description from a string representation.
        
        Args:
            value: String representation of the description.
            
        Returns:
            Description instance.
            
        Raises:
            ValueError: If the string is not a valid description.
        """
        try:
            return cls(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid description string: {value}") from e