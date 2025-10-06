"""Update category command.

This module contains the command for category update operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UpdateCategoryCommand:
    """Command for updating an existing category.
    
    This immutable command object carries all the necessary data
    for category update operations.
    
    Attributes:
        category_id: The ID of the category to update
        user_id: The ID of the user updating the category (for authorization)
        name: The new name for the category
    """
    
    category_id: str
    user_id: str
    name: str
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.category_id or not self.category_id.strip():
            raise ValueError("Category ID is required")
        
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
        
        if not self.name or not self.name.strip():
            raise ValueError("Category name is required")
        
        # Normalize name
        name = self.name.strip()
        object.__setattr__(self, 'name', name)
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"UpdateCategoryCommand(category_id={self.category_id}, user_id={self.user_id}, name={self.name})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"UpdateCategoryCommand(category_id='{self.category_id}', "
            f"user_id='{self.user_id}', name='{self.name}')"
        )