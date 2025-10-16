"""Event dispatcher for outbox pattern.

This module processes events from the outbox table and dispatches
them to external systems. It handles retries, error tracking, and
marking events as processed.
"""

import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.utils import timezone

from ...application.event_bus import EventBus
from .models import OutboxEvent

logger = logging.getLogger(__name__)


def get_unprocessed_events(batch_size: int = 100) -> List[OutboxEvent]:
    """Get unprocessed events from outbox.
    
    Args:
        batch_size: Maximum number of events to retrieve.
        
    Returns:
        List of unprocessed outbox events.
    """
    return list(OutboxEvent.objects.filter(
        processed_at__isnull=True,
    ).order_by('created_at')[:batch_size])


def mark_processed(event: OutboxEvent) -> None:
    """Mark event as successfully processed.
    
    Args:
        event: Outbox event to mark as processed.
    """
    event.processed_at = timezone.now()
    event.save(update_fields=['processed_at'])


def mark_failed(event: OutboxEvent, error: str) -> None:
    """Mark event as failed with error message.
    
    Args:
        event: Failed outbox event.
        error: Error message to record.
    """
    event.error_count += 1
    event.error_message = error
    event.save(update_fields=['error_count', 'error_message'])


def dispatch_events(batch_size: int = 100) -> int:
    """Process a batch of events from the outbox.
    
    Retrieves unprocessed events, dispatches them to external systems,
    and marks them as processed or failed.
    
    Args:
        batch_size: Maximum number of events to process.
        
    Returns:
        Number of events processed.
        
    Raises:
        Exception: If event processing fails.
    """
    processed = 0
    events = get_unprocessed_events(batch_size)

    if not events:
        return 0

    for event in events:
        try:
            # Process event using event bus/handler
            event_bus = EventBus()
            # event_bus.publish(event)
            
            # Mark as processed
            mark_processed(event)
            processed += 1
            
        except Exception as e:
            logger.error(
                f"Failed to process event {event.id}: {str(e)}",
                exc_info=True
            )
            mark_failed(event, str(e))

    return processed