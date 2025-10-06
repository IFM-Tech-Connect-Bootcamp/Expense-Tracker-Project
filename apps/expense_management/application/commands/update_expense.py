"""Update expense command.

This module contains the command for expense update operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True, slots=True)
class UpdateExpenseCommand:
    """Command for updating an existing expense.
    
    This immutable command object carries all the necessary data
    for expense update operations.
    
    Attributes:
        expense_id: The ID of the expense to update
        user_id: The ID of the user updating the expense (for authorization)
        category_id: Optional new category ID for the expense
        amount_tzs: Optional new amount in Tanzanian Shillings
        description: Optional new description of the expense
        expense_date: Optional new date when the expense occurred
    """
    
    expense_id: str
    user_id: str
    category_id: Optional[str] = None
    amount_tzs: Optional[float] = None
    description: Optional[str] = None
    expense_date: Optional[date] = None
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.expense_id or not self.expense_id.strip():
            raise ValueError("Expense ID is required")
        
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
        
        if self.amount_tzs is not None and self.amount_tzs < 0:
            raise ValueError("Amount must be non-negative")
        
        # Normalize category_id
        if self.category_id is not None:
            category_id = self.category_id.strip()
            if not category_id:
                object.__setattr__(self, 'category_id', None)
            else:
                object.__setattr__(self, 'category_id', category_id)
        
        # Normalize description  
        if self.description is not None:
            description = self.description.strip()
            if not description:
                object.__setattr__(self, 'description', None)
            else:
                object.__setattr__(self, 'description', description)
    
    def has_updates(self) -> bool:
        """Check if the command contains any update data."""
        return any([
            self.category_id is not None,
            self.amount_tzs is not None,
            self.description is not None,
            self.expense_date is not None
        ])
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"UpdateExpenseCommand(expense_id={self.expense_id}, user_id={self.user_id})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"UpdateExpenseCommand(expense_id='{self.expense_id}', "
            f"user_id='{self.user_id}', category_id='{self.category_id}', "
            f"amount_tzs={self.amount_tzs}, description='{self.description}', "
            f"expense_date={self.expense_date})"
        )