"""Expense entity - aggregate root for expense management.

This module contains the Expense entity which represents a single expense record
in the expense management bounded context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, Any, Optional, TYPE_CHECKING

from ..value_objects import (
    ExpenseId, CategoryId, UserId, AmountTZS, 
    ExpenseDescription
)

if TYPE_CHECKING:
    from ..events.expense_events import DomainEvent


@dataclass
class Expense:
    """Expense aggregate root entity.
    
    An expense represents a single spending transaction that belongs to exactly 
    one user and one category. It tracks spending in Tanzanian Shillings (TZS) 
    with an optional description and date.
    
    The Expense entity is responsible for:
    - Maintaining expense data integrity
    - Enforcing business rules for expense modifications
    - Managing expense state transitions
    - Publishing domain events for significant changes
    """
    
    expense_id: ExpenseId
    user_id: UserId
    category_id: CategoryId
    amount_tzs: AmountTZS
    description: ExpenseDescription
    expense_date: date
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _events: list[DomainEvent] = field(default_factory=list, init=False)

    def update_amount(self, new_amount: AmountTZS) -> None:
        """Update the expense amount.
        
        Args:
            new_amount: New amount for the expense.
            
        Raises:
            ValueError: If amount is invalid.
        """
        if not isinstance(new_amount, AmountTZS):
            raise ValueError("Amount must be an AmountTZS instance")
        
        previous_amount = self.amount_tzs
        self.amount_tzs = new_amount
        self.updated_at = datetime.now()
        
        # Record the change
        self._record_expense_updated(previous_amount)

    def update_description(self, new_description: ExpenseDescription) -> None:
        """Update the expense description.
        
        Args:
            new_description: New description for the expense.
        """
        if not isinstance(new_description, ExpenseDescription):
            raise ValueError("Description must be an ExpenseDescription instance")
        
        self.description = new_description
        self.updated_at = datetime.now()

    def update_category(self, new_category_id: CategoryId) -> None:
        """Update the expense category.
        
        Args:
            new_category_id: New category ID for the expense.
        """
        if not isinstance(new_category_id, CategoryId):
            raise ValueError("Category ID must be a CategoryId instance")
        
        self.category_id = new_category_id
        self.updated_at = datetime.now()

    def update_date(self, new_date: date) -> None:
        """Update the expense date.
        
        Args:
            new_date: New date for the expense.
        """
        if not isinstance(new_date, date):
            raise ValueError("Date must be a date instance")
        
        self.expense_date = new_date
        self.updated_at = datetime.now()

    def update(
        self, 
        amount_tzs: Optional[AmountTZS] = None,
        description: Optional[ExpenseDescription] = None,
        category_id: Optional[CategoryId] = None,
        expense_date: Optional[date] = None
    ) -> None:
        """Update multiple expense fields at once.
        
        Args:
            amount_tzs: Optional new amount.
            description: Optional new description.
            category_id: Optional new category ID.
            expense_date: Optional new expense date.
        """
        previous_amount = self.amount_tzs
        
        if amount_tzs is not None:
            self.amount_tzs = amount_tzs
        if description is not None:
            self.description = description
        if category_id is not None:
            self.category_id = category_id
        if expense_date is not None:
            self.expense_date = expense_date
        
        self.updated_at = datetime.now()
        
        # Record the change if amount was updated
        if amount_tzs is not None:
            self._record_expense_updated(previous_amount)

    def belongs_to(self, user_id: UserId) -> bool:
        """Check if this expense belongs to the specified user.
        
        Args:
            user_id: User ID to check ownership against.
            
        Returns:
            True if expense belongs to the user, False otherwise.
        """
        return self.user_id == user_id

    def is_in_category(self, category_id: CategoryId) -> bool:
        """Check if this expense is in the specified category.
        
        Args:
            category_id: Category ID to check against.
            
        Returns:
            True if expense is in the category, False otherwise.
        """
        return self.category_id == category_id

    def is_on_date(self, target_date: date) -> bool:
        """Check if this expense occurred on the specified date.
        
        Args:
            target_date: Date to check against.
            
        Returns:
            True if expense occurred on the date, False otherwise.
        """
        return self.expense_date == target_date

    def is_in_date_range(self, start_date: date, end_date: date) -> bool:
        """Check if this expense falls within the specified date range.
        
        Args:
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).
            
        Returns:
            True if expense is in the range, False otherwise.
        """
        return start_date <= self.expense_date <= end_date

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return the list of domain events.
        
        Returns:
            List of domain events that were cleared.
        """
        events = self._events.copy()
        self._events.clear()
        return events

    def to_dict(self) -> Dict[str, Any]:
        """Convert expense to dictionary for serialization.
        
        Returns:
            Dictionary representation of the expense.
        """
        return {
            'expense_id': str(self.expense_id),
            'user_id': str(self.user_id),
            'category_id': str(self.category_id),
            'amount_tzs': self.amount_tzs.to_float(),
            'description': str(self.description) if self.description.value else None,
            'expense_date': self.expense_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def _record_expense_updated(self, previous_amount: AmountTZS) -> None:
        """Record expense updated domain event.
        
        Args:
            previous_amount: Previous amount before the update.
        """
        from ..events.expense_events import ExpenseUpdated
        import uuid
        
        event = ExpenseUpdated(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.now(),
            aggregate_id=str(self.expense_id),
            event_type="ExpenseUpdated",
            user_id=self.user_id,
            category_id=self.category_id,
            amount_tzs=self.amount_tzs,
            description=str(self.description),
            expense_date=self.expense_date.isoformat(),
            previous_amount_tzs=previous_amount
        )
        self._events.append(event)

    @classmethod
    def create(
        cls,
        user_id: UserId,
        category_id: CategoryId,
        amount_tzs: AmountTZS,
        description: ExpenseDescription,
        expense_date: Optional[date] = None
    ) -> Expense:
        """Create a new expense with generated ID.
        
        Args:
            user_id: ID of the user who owns the expense.
            category_id: ID of the category for the expense.
            amount_tzs: Amount of the expense in TZS.
            description: Description of the expense.
            expense_date: Date of the expense (defaults to today).
            
        Returns:
            New Expense instance.
        """
        expense = cls(
            expense_id=ExpenseId.generate(),
            user_id=user_id,
            category_id=category_id,
            amount_tzs=amount_tzs,
            description=description,
            expense_date=expense_date or date.today()
        )
        
        # Record creation event
        expense._record_expense_created()
        
        return expense
    
    def _record_expense_created(self) -> None:
        """Record expense created domain event."""
        from ..events.expense_events import ExpenseCreated
        import uuid
        
        event = ExpenseCreated(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.now(),
            aggregate_id=str(self.expense_id),
            event_type="ExpenseCreated",
            user_id=self.user_id,
            category_id=self.category_id,
            amount_tzs=self.amount_tzs,
            description=str(self.description),
            expense_date=self.expense_date.isoformat()
        )
        self._events.append(event)