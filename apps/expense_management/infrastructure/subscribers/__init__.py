"""Event subscribers for Expense Management infrastructure.

This package contains event subscribers that handle domain events
and forward them to external systems via the outbox pattern.
"""

from .notify_on_expense_events import (
    on_expense_created,
    on_expense_updated,
    on_expense_deleted,
    on_category_created,
    on_category_updated,
    on_category_deleted,
)

# Keep the existing log function for backward compatibility
import logging
from typing import Any, Dict

try:
    from ...domain.events import (
        ExpenseCreated, ExpenseUpdated, ExpenseDeleted,
        CategoryCreated, CategoryUpdated, CategoryDeleted,
        DomainEvent
    )
except ImportError:
    # Fallback for when domain events are not available
    from typing import Protocol
    
    class DomainEvent(Protocol):
        event_id: str
        occurred_at: Any
    
    class ExpenseCreated(DomainEvent): pass
    class ExpenseUpdated(DomainEvent): pass  
    class ExpenseDeleted(DomainEvent): pass
    class CategoryCreated(DomainEvent): pass
    class CategoryUpdated(DomainEvent): pass
    class CategoryDeleted(DomainEvent): pass

logger = logging.getLogger(__name__)


def log_expense_events(event: DomainEvent) -> None:
    """Log expense-related domain events.
    
    Args:
        event: Domain event to log.
    """
    event_data = {
        'event_type': event.__class__.__name__,
        'event_id': event.event_id,
        'occurred_at': event.occurred_at.isoformat(),
        'entity_id': getattr(event, 'expense_id', getattr(event, 'category_id', None)),
    }
    
    if isinstance(event, (ExpenseCreated, ExpenseUpdated, ExpenseDeleted)):
        event_data['expense_id'] = event.expense_id
        logger.info(f"Expense event: {event.__class__.__name__}", extra=event_data)
    
    elif isinstance(event, (CategoryCreated, CategoryUpdated, CategoryDeleted)):
        event_data['category_id'] = event.category_id
        logger.info(f"Category event: {event.__class__.__name__}", extra=event_data)
    
    else:
        logger.info(f"Domain event: {event.__class__.__name__}", extra=event_data)


__all__ = [
    # Outbox integration subscribers (async)
    'on_expense_created',
    'on_expense_updated',
    'on_expense_deleted', 
    'on_category_created',
    'on_category_updated',
    'on_category_deleted',
    
    # Legacy logging subscriber (sync)
    'log_expense_events',
]