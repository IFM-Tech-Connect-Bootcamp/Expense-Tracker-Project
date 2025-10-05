"""Update profile command.

This module contains the command for user profile update operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class UpdateProfileCommand:
    """Command for updating a user's profile.
    
    This immutable command object carries all the necessary data
    for profile update operations.
    
    Attributes:
        user_id: The ID of the user updating their profile
        new_email: New email address (optional)
        new_first_name: New first name (optional)
        new_last_name: New last name (optional)
    """
    
    user_id: str
    new_email: Optional[str] = None
    new_first_name: Optional[str] = None
    new_last_name: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
        
        # At least one field must be provided for update
        if not any([
            self.new_email and self.new_email.strip(),
            self.new_first_name and self.new_first_name.strip(),
            self.new_last_name and self.new_last_name.strip()
        ]):
            raise ValueError("At least one field must be provided for update")
    
    def has_email_update(self) -> bool:
        """Check if email update is requested."""
        return self.new_email is not None and self.new_email.strip()
    
    def has_first_name_update(self) -> bool:
        """Check if first name update is requested."""
        return self.new_first_name is not None and self.new_first_name.strip()
    
    def has_last_name_update(self) -> bool:
        """Check if last name update is requested."""
        return self.new_last_name is not None and self.new_last_name.strip()
    
    def __str__(self) -> str:
        """Return string representation."""
        updates = []
        if self.has_email_update():
            updates.append("email")
        if self.has_first_name_update():
            updates.append("first_name")
        if self.has_last_name_update():
            updates.append("last_name")
        
        return f"UpdateProfileCommand(user_id={self.user_id}, updates={updates})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"UpdateProfileCommand(user_id='{self.user_id}', "
            f"new_email={self.new_email!r}, new_first_name={self.new_first_name!r}, "
            f"new_last_name={self.new_last_name!r})"
        )