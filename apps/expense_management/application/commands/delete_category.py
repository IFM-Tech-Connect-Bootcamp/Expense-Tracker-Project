"""Delete category command.

This module contains the command for category deletion operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeleteCategoryCommand:
    """Command for deleting a category.
    
    This immutable command object carries all the necessary data
    for category deletion operations.
    
    Attributes:
        category_id: The ID of the category to delete
        user_id: The ID of the user deleting the category (for authorization)
    """
    
    category_id: str
    user_id: str
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.category_id or not self.category_id.strip():
            raise ValueError("Category ID is required")
        
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"DeleteCategoryCommand(category_id={self.category_id}, user_id={self.user_id})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"DeleteCategoryCommand(category_id='{self.category_id}', "
            f"user_id='{self.user_id}')"
        )