"""Authenticate user command.

This module contains the command for user authentication operations.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    """Command for authenticating a user.
    
    This immutable command object carries all the necessary data
    for user authentication operations.
    
    Attributes:
        email: The user's email address
        password: The user's plain text password
    """
    
    email: str
    password: str
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.email or not self.email.strip():
            raise ValueError("Email is required")
        
        if not self.password or not self.password.strip():
            raise ValueError("Password is required")
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"AuthenticateUserCommand(email={self.email})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"AuthenticateUserCommand(email='{self.email}', password='***')"