"""Register user command.

This module contains the command for user registration operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    """Command for registering a new user.
    
    This immutable command object carries all the necessary data
    for user registration operations.
    
    Attributes:
        email: The user's email address
        password: The user's plain text password (will be hashed)
        first_name: The user's first name
        last_name: The user's last name
    """
    
    email: str
    password: str
    first_name: str
    last_name: str
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.email or not self.email.strip():
            raise ValueError("Email is required")
        
        if not self.password or not self.password.strip():
            raise ValueError("Password is required")
        
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name is required")
        
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name is required")
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"RegisterUserCommand(email={self.email}, first_name={self.first_name}, last_name={self.last_name})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"RegisterUserCommand(email='{self.email}', "
            f"first_name='{self.first_name}', last_name='{self.last_name}', "
            f"password='***')"
        )