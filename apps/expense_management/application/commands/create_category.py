"""Create category command.

This module contains the command for category creation operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateCategoryCommand:
    """Command for creating a new category.
    
    This immutable command object carries all the necessary data
    for category creation operations.
    
    Attributes:
        user_id: The ID of the user creating the category
        name: The name of the category
    """
    
    user_id: str
    name: str
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
        
        if not self.name or not self.name.strip():
            raise ValueError("Category name is required")
        
        # Normalize name
        name = self.name.strip()
        object.__setattr__(self, 'name', name)
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"CreateCategoryCommand(user_id={self.user_id}, name={self.name})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"CreateCategoryCommand(user_id='{self.user_id}', "
            f"name='{self.name}')"
        )