"""Expense status enumeration."""

from enum import Enum, unique
from typing import Self


@unique
class ExpenseStatus(Enum):
    """Enumeration of possible expense status values.
    
    This enum defines the status states an expense can be in within the system.
    For MVP, we only have active expenses, but this allows for future expansion.
    """
    
    ACTIVE = "active"
    ARCHIVED = "archived"
    
    def __str__(self) -> str:
        """Return the string value of the status."""
        return self.value
    
    def __repr__(self) -> str:
        """Return a detailed string representation."""
        return f"ExpenseStatus.{self.name}"
    
    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create an ExpenseStatus from a string value.
        
        Args:
            value: The string representation of the status.
            
        Returns:
            ExpenseStatus instance.
            
        Raises:
            ValueError: If the string doesn't match any status.
        """
        try:
            return cls(value.lower().strip())
        except ValueError as e:
            valid_values = [status.value for status in cls]
            raise ValueError(
                f"Invalid expense status: {value}. Valid values are: {valid_values}"
            ) from e
    
    @property
    def is_active(self) -> bool:
        """Check if the status represents an active expense.
        
        Returns:
            True if the expense is active, False otherwise.
        """
        return self == ExpenseStatus.ACTIVE
    
    @property
    def is_archived(self) -> bool:
        """Check if the status represents an archived expense.
        
        Returns:
            True if the expense is archived, False otherwise.
        """
        return self == ExpenseStatus.ARCHIVED