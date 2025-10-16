"""User entity - the aggregate root for user management.

This module contains the User entity which serves as the aggregate root
for the user management bounded context. It encapsulates all user-related
business logic and invariants.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from django.utils import timezone

from ..value_objects.user.user_id import UserId
from ..value_objects.expense.amount_tzs import AmountTZS
from ..value_objects.expense.description import Description
from ..value_objects.expense.date import Date
from ..value_objects.category.category_id import CategoryId
"""
from ..errors import (
    InvalidOperationError,
    DomainValidationError,
    PasswordPolicyError
)
"""
"""
if TYPE_CHECKING:
    from ..services.password_policy import PasswordHasher
    from ..events.user_events import DomainEvent
"""

@dataclass
class Expense:
    """Represents an expense entity with various attributes and validation."""
    
    expense_id: str
    user_id: UserId
    amount_tzs: AmountTZS
    description: Description
    date: Date
    category_id: Optional[CategoryId] = None
    created_at: datetime = field(default_factory=timezone.now)
    updated_at: datetime = field(default_factory=timezone.now)
    
    def update_amount(self, new_amount: AmountTZS) -> None:
        """Update the amount of the expense."""
        self.amount_tzs = new_amount
        self.updated_at = timezone.now()
    
    def update_description(self, new_description: Description) -> None:
        """Update the description of the expense."""
        self.description = new_description
        self.updated_at = timezone.now()
    
    def update_date(self, new_date: Date) -> None:
        """Update the date of the expense."""

        self.date = new_date
        self.updated_at = timezone.now()
    
    def update_category(self, new_category_id: Optional[CategoryId]) -> None:
        """Update the category of the expense."""
        self.category_id = new_category_id
        self.updated_at = timezone.now()

    def belongs_to_user(self, user_id: UserId) -> bool:
        """Check if the expense belongs to the given user."""
        return self.user_id == user_id