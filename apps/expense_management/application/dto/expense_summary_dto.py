"""Expense Summary Data Transfer Object.

This module contains the DTO for expense summary data representation
in the application layer responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional


@dataclass(frozen=True, slots=True)
class CategorySummaryDTO:
    """Data Transfer Object for category expense summary.
    
    Represents aggregated expense data for a specific category.
    
    Attributes:
        category_id: The category's unique identifier
        category_name: The name of the category
        total_amount_tzs: Total expenses in this category (TZS)
        expense_count: Number of expenses in this category
        average_amount_tzs: Average expense amount in this category (TZS)
    """
    
    category_id: str
    category_name: str
    total_amount_tzs: float
    expense_count: int
    average_amount_tzs: float
    
    def format_total_amount(self) -> str:
        """Format total amount as TZS currency string."""
        return f"TZS {self.total_amount_tzs:,.2f}"
    
    def format_average_amount(self) -> str:
        """Format average amount as TZS currency string."""
        return f"TZS {self.average_amount_tzs:,.2f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary representation."""
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'total_amount_tzs': self.total_amount_tzs,
            'expense_count': self.expense_count,
            'average_amount_tzs': self.average_amount_tzs
        }


@dataclass(frozen=True, slots=True)
class ExpenseSummaryDTO:
    """Data Transfer Object for expense summary and analytics.
    
    This DTO provides aggregated expense data for reporting and analytics
    in the application layer responses.
    
    Attributes:
        user_id: The ID of the user this summary belongs to
        total_amount_tzs: Total expense amount (TZS)
        total_expense_count: Total number of expenses
        average_expense_amount_tzs: Average expense amount (TZS)
        start_date: Start date of the summary period (if filtered)
        end_date: End date of the summary period (if filtered)
        category_summaries: List of per-category summaries
    """
    
    user_id: str
    total_amount_tzs: float
    total_expense_count: int
    average_expense_amount_tzs: float
    start_date: Optional[date]
    end_date: Optional[date]
    category_summaries: List[CategorySummaryDTO]
    
    def format_total_amount(self) -> str:
        """Format total amount as TZS currency string.
        
        Returns:
            Formatted amount string like "TZS 150,000.50"
        """
        return f"TZS {self.total_amount_tzs:,.2f}"
    
    def format_average_amount(self) -> str:
        """Format average amount as TZS currency string.
        
        Returns:
            Formatted amount string like "TZS 5,000.25"
        """
        return f"TZS {self.average_expense_amount_tzs:,.2f}"
    
    def get_top_categories(self, limit: int = 5) -> List[CategorySummaryDTO]:
        """Get top categories by total spending.
        
        Args:
            limit: Maximum number of categories to return.
            
        Returns:
            List of top category summaries sorted by total amount.
        """
        return sorted(
            self.category_summaries,
            key=lambda cat: cat.total_amount_tzs,
            reverse=True
        )[:limit]
    
    def has_date_filter(self) -> bool:
        """Check if summary includes date filtering."""
        return self.start_date is not None or self.end_date is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary representation.
        
        Returns:
            Dictionary representation of the expense summary data.
        """
        return {
            'user_id': self.user_id,
            'total_amount_tzs': self.total_amount_tzs,
            'total_expense_count': self.total_expense_count,
            'average_expense_amount_tzs': self.average_expense_amount_tzs,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'category_summaries': [cat.to_dict() for cat in self.category_summaries]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExpenseSummaryDTO:
        """Create DTO from dictionary representation.
        
        Args:
            data: Dictionary containing expense summary data.
            
        Returns:
            ExpenseSummaryDTO instance.
        """
        start_date = None
        if data.get('start_date'):
            start_date = date.fromisoformat(data['start_date'])
            
        end_date = None
        if data.get('end_date'):
            end_date = date.fromisoformat(data['end_date'])
        
        category_summaries = []
        for cat_data in data.get('category_summaries', []):
            category_summaries.append(CategorySummaryDTO(**cat_data))
        
        return cls(
            user_id=data['user_id'],
            total_amount_tzs=data['total_amount_tzs'],
            total_expense_count=data['total_expense_count'],
            average_expense_amount_tzs=data['average_expense_amount_tzs'],
            start_date=start_date,
            end_date=end_date,
            category_summaries=category_summaries
        )
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"ExpenseSummaryDTO(user_id={self.user_id}, total_amount_tzs={self.total_amount_tzs}, expense_count={self.total_expense_count})"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"ExpenseSummaryDTO(user_id='{self.user_id}', "
            f"total_amount_tzs={self.total_amount_tzs}, "
            f"total_expense_count={self.total_expense_count}, "
            f"average_expense_amount_tzs={self.average_expense_amount_tzs})"
        )