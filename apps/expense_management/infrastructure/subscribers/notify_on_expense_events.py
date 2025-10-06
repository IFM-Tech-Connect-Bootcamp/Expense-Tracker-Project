"""Infrastructure subscriber for expense management events.

This subscriber handles expense and category domain events and writes
them to the outbox for external system delivery.
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from ...domain.events import (
        ExpenseCreated, ExpenseUpdated, ExpenseDeleted,
        CategoryCreated, CategoryUpdated, CategoryDeleted,
        DomainEvent
    )
    EVENTS_AVAILABLE = True
except ImportError:
    # Fallback for when domain events are not available
    EVENTS_AVAILABLE = False
    DomainEvent = Any

from ..outbox.writer import write_domain_event

logger = logging.getLogger(__name__)


async def on_expense_created(event: Any) -> None:
    """Handle ExpenseCreated domain event.
    
    Writes the event to the outbox for reliable delivery to external systems.
    This enables decoupled integration with external services like:
    - Financial reporting systems
    - Analytics and business intelligence
    - Accounting software integration  
    - Tax preparation systems
    - Expense policy enforcement
    - Notification services
    
    Args:
        event: ExpenseCreated domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling ExpenseCreated event for expense: {getattr(event, 'expense_id', 'unknown')}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote ExpenseCreated event to outbox: {getattr(event, 'expense_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to write ExpenseCreated event to outbox: {e}")
        # Re-raise to ensure the error is visible to the event bus
        raise


async def on_expense_updated(event: Any) -> None:
    """Handle ExpenseUpdated domain event.
    
    Writes the event to the outbox for audit and compliance purposes.
    
    Args:
        event: ExpenseUpdated domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling ExpenseUpdated event for expense: {getattr(event, 'expense_id', 'unknown')}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote ExpenseUpdated event to outbox: {getattr(event, 'expense_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to write ExpenseUpdated event to outbox: {e}")
        raise


async def on_expense_deleted(event: Any) -> None:
    """Handle ExpenseDeleted domain event.
    
    Writes the event to the outbox for audit trail and compliance.
    
    Args:
        event: ExpenseDeleted domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling ExpenseDeleted event for expense: {getattr(event, 'expense_id', 'unknown')}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote ExpenseDeleted event to outbox: {getattr(event, 'expense_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to write ExpenseDeleted event to outbox: {e}")
        raise


async def on_category_created(event: Any) -> None:
    """Handle CategoryCreated domain event.
    
    Writes the event to the outbox for category management integrations.
    
    Args:
        event: CategoryCreated domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling CategoryCreated event for category: {getattr(event, 'category_id', 'unknown')}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote CategoryCreated event to outbox: {getattr(event, 'category_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to write CategoryCreated event to outbox: {e}")
        raise


async def on_category_updated(event: Any) -> None:
    """Handle CategoryUpdated domain event.
    
    Writes the event to the outbox for category synchronization.
    
    Args:
        event: CategoryUpdated domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling CategoryUpdated event for category: {getattr(event, 'category_id', 'unknown')}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote CategoryUpdated event to outbox: {getattr(event, 'category_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to write CategoryUpdated event to outbox: {e}")
        raise


async def on_category_deleted(event: Any) -> None:
    """Handle CategoryDeleted domain event.
    
    Writes the event to the outbox for category cleanup and audit.
    
    Args:
        event: CategoryDeleted domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling CategoryDeleted event for category: {getattr(event, 'category_id', 'unknown')}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote CategoryDeleted event to outbox: {getattr(event, 'category_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to write CategoryDeleted event to outbox: {e}")
        raise