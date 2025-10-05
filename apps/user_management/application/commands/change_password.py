"""Change password command.

This module contains the command for password change operations.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChangePasswordCommand:
    """Command for changing a user's password.
    
    This immutable command object carries all the necessary data
    for password change operations.
    
    Attributes:
        user_id: The ID of the user changing their password
        old_password: The user's current password
        new_password: The user's new password
    """
    
    user_id: str
    old_password: str
    new_password: str
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
        
        if not self.old_password or not self.old_password.strip():
            raise ValueError("Old password is required")
        
        if not self.new_password or not self.new_password.strip():
            raise ValueError("New password is required")
        
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from old password")
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"ChangePasswordCommand(user_id={self.user_id})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"ChangePasswordCommand(user_id='{self.user_id}', "
            f"old_password='***', new_password='***')"
        )