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

from .models import OutboxEvent

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
    
    def _write_event() -> OutboxEvent:
        event = OutboxEvent.objects.create(
            event_type=event_type,
            aggregate_id=aggregate_id,
            payload=payload,
        )
        logger.info(f"Wrote outbox event {event.id}: {event_type}")
        return event
    
    if use_transaction_commit:
        # Write event on successful transaction commit
        event = None
        def _commit_callback():
            nonlocal event
            event = _write_event()
        transaction.on_commit(_commit_callback)
        return event  # type: ignore
    else:
        # Write event immediately
        return _write_event()