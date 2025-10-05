"""Email value object with validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Self


@dataclass(frozen=True, slots=True)
class Email:
    """A validated email address value object.
    
    This value object ensures email addresses are syntactically valid
    and provides type safety for email operations.
    """
    
    # RFC 5322 compliant regex (simplified but robust)
    _EMAIL_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )
    
    value: str
    
    
    
    
    def __post_init__(self) -> None:
        """Validate the email format."""
        if not isinstance(self.value, str):
            raise TypeError("Email value must be a string")
        
        if not self.value.strip():
            raise ValueError("Email cannot be empty")
        
        # Normalize the email (lowercase and strip whitespace)
        normalized = self.value.strip().lower()
        object.__setattr__(self, 'value', normalized)
        
        if len(normalized) > 254:  # RFC 5321 limit
            raise ValueError("Email address is too long (max 254 characters)")
        
        if not self._EMAIL_REGEX.match(normalized):
            raise ValueError(f"Invalid email format: {normalized}")
    
    
    
    
    
    @classmethod
    def create(cls, value: str) -> Self:
        """Create an Email instance with explicit validation.
        
        Args:
            value: The email string to validate.
            
        Returns:
            Email instance.
            
        Raises:
            ValueError: If the email format is invalid.
            TypeError: If value is not a string.
        """
        return cls(value)
    
    
    
    
    @property
    def domain(self) -> str:
        """Extract the domain part of the email.
        
        Returns:
            The domain portion of the email address.
        """
        return self.value.split('@')[1]
    
    
    
    
    
    @property
    def local_part(self) -> str:
        """Extract the local part of the email.
        
        Returns:
            The local portion (before @) of the email address.
        """
        return self.value.split('@')[0]
    
    
    
    
    def __str__(self) -> str:
        """Return string representation of the email."""
        return self.value
    
    
    
    
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"Email('{self.value}')"