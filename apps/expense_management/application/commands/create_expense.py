"""Create expense command.

This module contains the command for expense creation operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True, slots=True)
class CreateExpenseCommand:
    """Command for creating a new expense.
    
    This immutable command object carries all the necessary data
    for expense creation operations.
    
    Attributes:
        user_id: The ID of the user creating the expense
        category_id: The ID of the category for this expense
        amount_tzs: The expense amount in Tanzanian Shillings
        description: Optional description of the expense
        expense_date: The date when the expense occurred
    """
    
    user_id: str
    category_id: str
    amount_tzs: float
    description: Optional[str] = None
    expense_date: Optional[date] = None
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
        
        if not self.category_id or not self.category_id.strip():
            raise ValueError("Category ID is required")
        
        if self.amount_tzs is None or self.amount_tzs < 0:
            raise ValueError("Amount must be non-negative")
        
        # Set default expense date to today if not provided
        if self.expense_date is None:
            object.__setattr__(self, 'expense_date', date.today())
        
        # Normalize description
        if self.description is not None:
            description = self.description.strip()
            if not description:
                object.__setattr__(self, 'description', None)
            else:
                object.__setattr__(self, 'description', description)
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"CreateExpenseCommand(user_id={self.user_id}, category_id={self.category_id}, amount_tzs={self.amount_tzs})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"CreateExpenseCommand(user_id='{self.user_id}', "
            f"category_id='{self.category_id}', amount_tzs={self.amount_tzs}, "
            f"description='{self.description}', expense_date={self.expense_date})"
        )