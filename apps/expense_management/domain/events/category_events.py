"""
Expense Management Domain - Category Events

This module contains category-related domain events for the expense management bounded context.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from ..value_objects import CategoryId, UserId
from .expense_events import DomainEvent


@dataclass(frozen=True)
class CategoryCreated(DomainEvent):
    """Event raised when a new category is created."""
    user_id: UserId
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': str(self.user_id),
            'name': self.name
        })
        return base_dict


@dataclass(frozen=True)
class CategoryUpdated(DomainEvent):
    """Event raised when a category is updated."""
    user_id: UserId
    name: str
    previous_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': str(self.user_id),
            'name': self.name,
            'previous_name': self.previous_name
        })
        return base_dict


@dataclass(frozen=True)
class CategoryDeleted(DomainEvent):
    """Event raised when a category is deleted."""
    user_id: UserId
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'user_id': str(self.user_id),
            'name': self.name
        })
        return base_dict