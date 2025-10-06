"""Expense Data Transfer Object.

This module contains the DTO for expense data representation
in the application layer responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, Any, Optional


@dataclass(frozen=True, slots=True)
class ExpenseDTO:
    """Data Transfer Object for Expense entity.
    
    This DTO provides a flat, presentation-ready representation
    of expense data for API responses and inter-layer communication.
    
    Attributes:
        id: The expense's unique identifier
        user_id: The ID of the user who owns this expense
        category_id: The ID of the category for this expense
        amount_tzs: The expense amount in Tanzanian Shillings
        description: Optional description of the expense
        expense_date: The date when the expense occurred
        created_at: When the expense was created
        updated_at: When the expense was last updated
    """
    
    id: str
    user_id: str
    category_id: str
    amount_tzs: float
    description: Optional[str]
    expense_date: date
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary representation.
        
        Returns:
            Dictionary representation of the expense data.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'amount_tzs': self.amount_tzs,
            'description': self.description,
            'expense_date': self.expense_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExpenseDTO:
        """Create DTO from dictionary representation.
        
        Args:
            data: Dictionary containing expense data.
            
        Returns:
            ExpenseDTO instance.
        """
        expense_date = data['expense_date']
        if isinstance(expense_date, str):
            expense_date = date.fromisoformat(expense_date)
            
        created_at = data['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
        updated_at = data['updated_at']
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            category_id=data['category_id'],
            amount_tzs=data['amount_tzs'],
            description=data.get('description'),
            expense_date=expense_date,
            created_at=created_at,
            updated_at=updated_at
        )
    
    def format_amount(self) -> str:
        """Format amount as TZS currency string.
        
        Returns:
            Formatted amount string like "TZS 15,000.50"
        """
        return f"TZS {self.amount_tzs:,.2f}"
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"ExpenseDTO(id={self.id}, amount_tzs={self.amount_tzs}, expense_date={self.expense_date})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"ExpenseDTO(id='{self.id}', user_id='{self.user_id}', "
            f"category_id='{self.category_id}', amount_tzs={self.amount_tzs}, "
            f"description='{self.description}', expense_date={self.expense_date})"
        )