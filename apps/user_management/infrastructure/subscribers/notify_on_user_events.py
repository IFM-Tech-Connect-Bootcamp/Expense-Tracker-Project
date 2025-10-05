"""Infrastructure subscriber for user registration events.

This subscriber handles UserRegistered domain events and writes
them to the outbox for external system delivery.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from ...domain.events.user_events import UserRegistered
from ..outbox.writer import write_domain_event

logger = logging.getLogger(__name__)


async def on_user_registered(event: UserRegistered) -> None:
    """Handle UserRegistered domain event.
    
    Writes the event to the outbox for reliable delivery to external systems.
    This enables decoupled integration with external services like:
    - Email notification services
    - Analytics systems
    - Customer management systems
    - Audit logging systems
    
    Args:
        event: UserRegistered domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling UserRegistered event for user: {event.aggregate_id}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote UserRegistered event to outbox: {event.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to write UserRegistered event to outbox: {e}")
        # Re-raise to ensure the error is visible to the event bus
        raise


async def on_user_password_changed(event: Any) -> None:
    """Handle UserPasswordChanged domain event.
    
    Writes the event to the outbox for security audit and notification purposes.
    
    Args:
        event: UserPasswordChanged domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling UserPasswordChanged event for user: {event.aggregate_id}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote UserPasswordChanged event to outbox: {event.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to write UserPasswordChanged event to outbox: {e}")
        raise


async def on_user_profile_updated(event: Any) -> None:
    """Handle UserProfileUpdated domain event.
    
    Writes the event to the outbox for profile change notifications and auditing.
    
    Args:
        event: UserProfileUpdated domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling UserProfileUpdated event for user: {event.aggregate_id}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote UserProfileUpdated event to outbox: {event.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to write UserProfileUpdated event to outbox: {e}")
        raise


async def on_user_deactivated(event: Any) -> None:
    """Handle UserDeactivated domain event.
    
    Writes the event to the outbox for account closure notifications and cleanup.
    
    Args:
        event: UserDeactivated domain event.
        
    Raises:
        Exception: If outbox writing fails.
    """
    logger.info(f"Handling UserDeactivated event for user: {event.aggregate_id}")
    
    try:
        # Write event to outbox for reliable delivery
        await write_domain_event(event, use_transaction_commit=True)
        
        logger.debug(f"Successfully wrote UserDeactivated event to outbox: {event.aggregate_id}")
        
    except Exception as e:
        logger.error(f"Failed to write UserDeactivated event to outbox: {e}")
        raise