"""Outbox event writer for reliable event delivery.

This module provides functionality to write domain events to the outbox
table for reliable delivery to external systems using the transactional
outbox pattern.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from ..orm.models import OutboxEvent

logger = logging.getLogger(__name__)


def write_outbox_event(
    event_type: str,
    aggregate_id: Optional[UUID] = None,
    payload: Optional[Dict[str, Any]] = None,
    use_transaction_commit: bool = True
) -> OutboxEvent:
    """Write a domain event to the outbox for reliable delivery.
    
    Args:
        event_type: Type/name of the domain event.
        aggregate_id: ID of the aggregate that generated the event.
        payload: Event data as dictionary.
        use_transaction_commit: If True, uses transaction.on_commit for reliability.
        
    Returns:
        Created OutboxEvent instance.
        
    Raises:
        ValueError: If event data is invalid.
    """
    if not event_type:
        raise ValueError("Event type cannot be empty")
    
    if payload is None:
        payload = {}
    
    logger.debug(f"Writing outbox event: {event_type}, aggregate: {aggregate_id}")
    
    try:
        # Validate payload can be serialized to JSON
        json.dumps(payload)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Event payload is not JSON serializable: {e}") from e
    
    def _create_event() -> OutboxEvent:
        """Internal function to create the outbox event."""
        event = OutboxEvent(
            event_type=event_type,
            aggregate_id=aggregate_id,
            payload=payload,
            created_at=timezone.now(),
            attempts=0
        )
        return event
    
    if use_transaction_commit:
        # Use transaction.on_commit to ensure event is only written
        # after the main transaction commits successfully
        def _save_on_commit():
            event = _create_event()
            event.save()
            logger.debug(f"Outbox event saved on commit: {event.id}")
        
        transaction.on_commit(_save_on_commit)
        
        # Return a temporary event for immediate use (won't have ID)
        temp_event = _create_event()
        logger.debug(f"Outbox event scheduled for commit: {event_type}")
        return temp_event
    else:
        # Save immediately within current transaction
        event = _create_event()
        event.save()
        logger.debug(f"Outbox event saved immediately: {event.id}")
        return event


def write_domain_event(
    domain_event: Any,
    use_transaction_commit: bool = True
) -> OutboxEvent:
    """Write a domain event object to the outbox.
    
    Args:
        domain_event: Domain event object with to_dict() method.
        use_transaction_commit: If True, uses transaction.on_commit for reliability.
        
    Returns:
        Created OutboxEvent instance.
        
    Raises:
        ValueError: If domain event is invalid.
    """
    if not hasattr(domain_event, 'to_dict'):
        raise ValueError("Domain event must have to_dict() method")
    
    try:
        event_type = domain_event.__class__.__name__
        payload = domain_event.to_dict()
        
        # Extract aggregate ID if available
        aggregate_id = None
        if hasattr(domain_event, 'aggregate_id'):
            aggregate_id = getattr(domain_event, 'aggregate_id')
            if hasattr(aggregate_id, 'value'):
                aggregate_id = aggregate_id.value
        
        return write_outbox_event(
            event_type=event_type,
            aggregate_id=aggregate_id,
            payload=payload,
            use_transaction_commit=use_transaction_commit
        )
        
    except Exception as e:
        logger.error(f"Failed to write domain event to outbox: {e}")
        raise ValueError(f"Failed to write domain event: {e}") from e


def write_multiple_events(
    events: list[Any],
    use_transaction_commit: bool = True
) -> list[OutboxEvent]:
    """Write multiple domain events to the outbox.
    
    Args:
        events: List of domain event objects.
        use_transaction_commit: If True, uses transaction.on_commit for reliability.
        
    Returns:
        List of created OutboxEvent instances.
        
    Raises:
        ValueError: If any event is invalid.
    """
    if not events:
        return []
    
    logger.debug(f"Writing {len(events)} events to outbox")
    
    outbox_events = []
    for event in events:
        outbox_event = write_domain_event(
            event,
            use_transaction_commit=use_transaction_commit
        )
        outbox_events.append(outbox_event)
    
    logger.debug(f"Successfully wrote {len(outbox_events)} events to outbox")
    return outbox_events


class OutboxEventWriter:
    """Service class for writing events to outbox.
    
    Provides a cleaner interface for dependency injection
    and configuration management.
    """
    
    def __init__(self, use_transaction_commit: bool = True) -> None:
        """Initialize outbox event writer.
        
        Args:
            use_transaction_commit: Default transaction commit behavior.
        """
        self._use_transaction_commit = use_transaction_commit
    
    def write_event(
        self,
        event_type: str,
        aggregate_id: Optional[UUID] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> OutboxEvent:
        """Write an event to the outbox.
        
        Args:
            event_type: Type of the event.
            aggregate_id: ID of the aggregate.
            payload: Event data.
            
        Returns:
            Created OutboxEvent instance.
        """
        return write_outbox_event(
            event_type=event_type,
            aggregate_id=aggregate_id,
            payload=payload,
            use_transaction_commit=self._use_transaction_commit
        )
    
    def write_domain_event(self, domain_event: Any) -> OutboxEvent:
        """Write a domain event to the outbox.
        
        Args:
            domain_event: Domain event object.
            
        Returns:
            Created OutboxEvent instance.
        """
        return write_domain_event(
            domain_event,
            use_transaction_commit=self._use_transaction_commit
        )
    
    def write_events(self, events: list[Any]) -> list[OutboxEvent]:
        """Write multiple events to the outbox.
        
        Args:
            events: List of domain events.
            
        Returns:
            List of created OutboxEvent instances.
        """
        return write_multiple_events(
            events,
            use_transaction_commit=self._use_transaction_commit
        )


# Factory function for dependency injection
def create_outbox_writer(use_transaction_commit: bool = True) -> OutboxEventWriter:
    """Create an outbox event writer with specified configuration.
    
    Args:
        use_transaction_commit: Whether to use transaction.on_commit.
        
    Returns:
        Configured outbox event writer instance.
    """
    return OutboxEventWriter(use_transaction_commit=use_transaction_commit)