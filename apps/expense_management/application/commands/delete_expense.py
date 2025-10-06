"""Delete expense command.

This module contains the command for expense deletion operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeleteExpenseCommand:
    """Command for deleting an expense.
    
    This immutable command object carries all the necessary data
    for expense deletion operations.
    
    Attributes:
        expense_id: The ID of the expense to delete
        user_id: The ID of the user deleting the expense (for authorization)
    """
    
    expense_id: str
    user_id: str
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.expense_id or not self.expense_id.strip():
            raise ValueError("Expense ID is required")
        
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"DeleteExpenseCommand(expense_id={self.expense_id}, user_id={self.user_id})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"DeleteExpenseCommand(expense_id='{self.expense_id}', "
            f"user_id='{self.user_id}')"
        )