"""Date value object with validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Self


@dataclass(frozen=True, slots=True)
class Date:
    """A value object representing a date.
    
    This class ensures that the date is in the format YYYY-MM-DD.
    """
    
    value: str
    DATE_REGEX: ClassVar[re.Pattern] = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    
    
    
    def __post_init__(self) -> None:
        """Validate the date value."""
        if not isinstance(self.value, str):
            raise TypeError("Date value must be a string")
        if not self.DATE_REGEX.match(self.value):
            raise ValueError("Date value must be in the format YYYY-MM-DD")
    
    
    
    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create a Date from a string representation.
        
        Args:
            value: String representation of the date.
            
        Returns:
            Date instance.
            
        Raises:
            ValueError: If the string is not a valid date.
        """
        try:
            return cls(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date string: {value}") from e