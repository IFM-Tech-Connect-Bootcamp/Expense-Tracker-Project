"""Deactivate user command.

This module contains the command for user deactivation operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class DeactivateUserCommand:
    """Command for deactivating a user account.
    
    This immutable command object carries all the necessary data
    for user deactivation operations.
    
    Attributes:
        user_id: The ID of the user to deactivate
        reason: Optional reason for deactivation
    """
    
    user_id: str
    reason: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"DeactivateUserCommand(user_id={self.user_id})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"DeactivateUserCommand(user_id='{self.user_id}', "
            f"reason={self.reason!r})"
        )