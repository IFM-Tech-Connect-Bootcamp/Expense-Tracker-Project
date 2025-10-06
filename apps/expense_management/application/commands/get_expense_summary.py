"""Get expense summary command.

This module contains the command for expense summary query operations.
Commands are immutable input contracts for use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True, slots=True)
class GetExpenseSummaryCommand:
    """Command for getting expense summary and analytics.
    
    This immutable command object carries all the necessary data
    for expense summary query operations.
    
    Attributes:
        user_id: The ID of the user requesting the summary
        start_date: Optional start date for filtering expenses
        end_date: Optional end date for filtering expenses
        category_id: Optional category ID for filtering expenses
    """
    
    user_id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate command data."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID is required")
        
        # Validate date range
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Normalize category_id
        if self.category_id is not None:
            category_id = self.category_id.strip()
            if not category_id:
                object.__setattr__(self, 'category_id', None)
            else:
                object.__setattr__(self, 'category_id', category_id)
    
    def has_date_filter(self) -> bool:
        """Check if the command has date filtering."""
        return self.start_date is not None or self.end_date is not None
    
    def has_category_filter(self) -> bool:
        """Check if the command has category filtering."""
        return self.category_id is not None
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"GetExpenseSummaryCommand(user_id={self.user_id})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"GetExpenseSummaryCommand(user_id='{self.user_id}', "
            f"start_date={self.start_date}, end_date={self.end_date}, "
            f"category_id='{self.category_id}')"
        )