"""Event subscribers for expense management events.

This module provides subscribers for handling domain events from
expense management bounded context. These subscribers handle the
side effects of domain events.
"""

import logging
from typing import Any, Dict

from ...domain.events.expense_events import ExpenseCreated, ExpenseUpdated
from ..outbox.writer import write_outbox_event

logger = logging.getLogger(__name__)


def on_expense_created(event: ExpenseCreated) -> None:
    """Handle expense created event.
    
    Args:
        event: Expense created domain event.
    """
    logger.info(
        f"Expense created: {event.expense_id}, user: {event.user_id}, "
        f"amount: {event.amount_tzs}"
    )
    
    # Write to outbox for external integrations
    write_outbox_event(
        event_type='expense.created',
        aggregate_id=event.expense_id.value,
        payload={
            'expense_id': str(event.expense_id),
            'user_id': str(event.user_id),
            'amount_tzs': float(event.amount_tzs) if event.amount_tzs is not None else 0.0,
            'description': str(event.description),
            'date': str(event.date),
            'category_id': str(event.category_id) if event.category_id else None,
        }
    )


def on_expense_updated(event: ExpenseUpdated) -> None:
    """Handle expense updated event.
    
    Args:
        event: Expense updated domain event.
    """
    logger.info(
        f"Expense updated: {event.expense_id}, user: {event.user_id}, "
        f"amount: {event.amount_tzs}"
    )
    
    # Write to outbox for external integrations  
    write_outbox_event(
        event_type='expense.updated',
        aggregate_id=event.expense_id.value,
        payload={
            'expense_id': str(event.expense_id),
            'user_id': str(event.user_id),
            'amount_tzs': float(event.amount_tzs if event.amount_tzs is not None else 0.0,),
            'description': str(event.description),
            'date': str(event.date),
            'category_id': str(event.category_id) if event.category_id else None,
        }
    )