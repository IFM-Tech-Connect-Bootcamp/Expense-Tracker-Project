"""
Expense Management Domain - Domain Events

This module contains domain events for the expense management bounded context.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from ..value_objects import ExpenseId, CategoryId, UserId, AmountTZS


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""
    event_id: str
    occurred_at: datetime
    aggregate_id: str
    event_type: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': self.aggregate_id,
            'event_type': self.event_type
        }


@dataclass(frozen=True)
class ExpenseCreated(DomainEvent):
    """Event raised when a new expense is created."""
    user_id: UserId
    category_id: CategoryId
    amount_tzs: AmountTZS
    description: str
    expense_date: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': str(self.user_id),
            'category_id': str(self.category_id),
            'amount_tzs': self.amount_tzs.to_float(),
            'description': self.description,
            'expense_date': self.expense_date
        })
        return base_dict


@dataclass(frozen=True)
class ExpenseUpdated(DomainEvent):
    """Event raised when an expense is updated."""
    user_id: UserId
    category_id: CategoryId
    amount_tzs: AmountTZS
    description: str
    expense_date: str
    previous_amount_tzs: AmountTZS

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': str(self.user_id),
            'category_id': str(self.category_id),
            'amount_tzs': self.amount_tzs.to_float(),
            'description': self.description,
            'expense_date': self.expense_date,
            'previous_amount_tzs': self.previous_amount_tzs.to_float()
        })
        return base_dict


@dataclass(frozen=True)
class ExpenseDeleted(DomainEvent):
    """Event raised when an expense is deleted."""
    user_id: UserId
    category_id: CategoryId
    amount_tzs: AmountTZS

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': str(self.user_id),
            'category_id': str(self.category_id),
            'amount_tzs': self.amount_tzs.to_float()
        })
        return base_dict