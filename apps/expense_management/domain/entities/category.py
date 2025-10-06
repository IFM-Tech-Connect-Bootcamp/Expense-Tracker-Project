"""Category entity for expense categorization.

This module contains the Category entity for the expense management bounded context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING

from ..value_objects import CategoryId, UserId, CategoryName

if TYPE_CHECKING:
    from ..events.category_events import DomainEvent


@dataclass
class Category:
    """Category entity for expense organization.
    
    Categories belong to a user and are used to organize expenses.
    Each user can have their own set of categories with unique names.
    
    The Category entity is responsible for:
    - Maintaining category data integrity
    - Enforcing business rules for category modifications
    - Managing category state transitions
    - Publishing domain events for significant changes
    """
    
    category_id: CategoryId
    user_id: UserId
    name: CategoryName
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _events: list[DomainEvent] = field(default_factory=list, init=False)

    def rename(self, new_name: CategoryName) -> None:
        """Rename the category.
        
        Args:
            new_name: New name for the category.
            
        Raises:
            ValueError: If new_name is invalid.
        """
        if not isinstance(new_name, CategoryName):
            raise ValueError("Name must be a CategoryName instance")
        
        previous_name = self.name.value
        self.name = new_name
        self.updated_at = datetime.now()
        
        # Record the change
        self._record_category_updated(previous_name)

    def belongs_to(self, user_id: UserId) -> bool:
        """Check if this category belongs to the specified user.
        
        Args:
            user_id: User ID to check ownership against.
            
        Returns:
            True if category belongs to the user, False otherwise.
        """
        return self.user_id == user_id

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return the list of domain events.
        
        Returns:
            List of domain events that were cleared.
        """
        events = self._events.copy()
        self._events.clear()
        return events

    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary for serialization.
        
        Returns:
            Dictionary representation of the category.
        """
        return {
            'category_id': str(self.category_id),
            'user_id': str(self.user_id),
            'name': str(self.name),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def _record_category_updated(self, previous_name: str) -> None:
        """Record category updated domain event.
        
        Args:
            previous_name: Previous name before the update.
        """
        from ..events.category_events import CategoryUpdated
        import uuid
        
        event = CategoryUpdated(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.now(),
            aggregate_id=str(self.category_id),
            event_type="CategoryUpdated",
            user_id=self.user_id,
            name=str(self.name),
            previous_name=previous_name
        )
        self._events.append(event)

    @classmethod
    def create(
        cls,
        user_id: UserId,
        name: CategoryName
    ) -> Category:
        """Create a new category with generated ID.
        
        Args:
            user_id: ID of the user who owns the category.
            name: Name of the category.
            
        Returns:
            New Category instance.
        """
        category = cls(
            category_id=CategoryId.generate(),
            user_id=user_id,
            name=name
        )
        
        # Record creation event
        category._record_category_created()
        
        return category
    
    def _record_category_created(self) -> None:
        """Record category created domain event."""
        from ..events.category_events import CategoryCreated
        import uuid
        
        event = CategoryCreated(
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.now(),
            aggregate_id=str(self.category_id),
            event_type="CategoryCreated",
            user_id=self.user_id,
            name=str(self.name)
        )
        self._events.append(event)