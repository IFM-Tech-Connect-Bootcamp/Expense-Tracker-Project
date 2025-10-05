"""Outbox event dispatcher for processing and delivering events.

This module provides functionality to process outbox events and deliver
them to external systems with retry logic and error handling.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Protocol

from django.db import models, transaction
from django.utils import timezone

from ..orm.models import OutboxEvent

logger = logging.getLogger(__name__)


class EventHandler(Protocol):
    """Protocol for event handlers that process outbox events."""
    
    async def handle(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Handle an outbox event.
        
        Args:
            event_type: Type of the event.
            payload: Event data.
            
        Raises:
            Exception: If event processing fails.
        """
        ...


class OutboxDispatcher:
    """Dispatcher for processing and delivering outbox events.
    
    Processes unprocessed outbox events and delivers them to
    registered event handlers with retry logic.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay_minutes: int = 5,
        batch_size: int = 50
    ) -> None:
        """Initialize outbox dispatcher.
        
        Args:
            max_retries: Maximum number of retry attempts per event.
            retry_delay_minutes: Delay between retries in minutes.
            batch_size: Number of events to process in each batch.
        """
        self._max_retries = max_retries
        self._retry_delay_minutes = retry_delay_minutes
        self._batch_size = batch_size
        self._handlers: Dict[str, EventHandler] = {}
        
        logger.debug(
            f"Initialized OutboxDispatcher: max_retries={max_retries}, "
            f"retry_delay={retry_delay_minutes}min, batch_size={batch_size}"
        )
    
    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register an event handler for a specific event type.
        
        Args:
            event_type: Type of events to handle.
            handler: Event handler instance.
        """
        self._handlers[event_type] = handler
        logger.debug(f"Registered handler for event type: {event_type}")
    
    def unregister_handler(self, event_type: str) -> None:
        """Unregister an event handler.
        
        Args:
            event_type: Type of events to stop handling.
        """
        if event_type in self._handlers:
            del self._handlers[event_type]
            logger.debug(f"Unregistered handler for event type: {event_type}")
    
    async def flush_outbox(self) -> Dict[str, int]:
        """Process unprocessed outbox events.
        
        Returns:
            Dictionary with processing statistics:
            - processed: Number of successfully processed events
            - failed: Number of events that failed processing
            - skipped: Number of events skipped (no handler or max retries exceeded)
        """
        logger.info("Starting outbox flush operation")
        
        stats = {
            'processed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # Get unprocessed events
            unprocessed_events = await self._get_unprocessed_events()
            
            if not unprocessed_events:
                logger.debug("No unprocessed events found")
                return stats
            
            logger.info(f"Processing {len(unprocessed_events)} outbox events")
            
            # Process events in batches
            for i in range(0, len(unprocessed_events), self._batch_size):
                batch = unprocessed_events[i:i + self._batch_size]
                batch_stats = await self._process_batch(batch)
                
                # Update overall stats
                for key in stats:
                    stats[key] += batch_stats[key]
            
            logger.info(
                f"Outbox flush completed: processed={stats['processed']}, "
                f"failed={stats['failed']}, skipped={stats['skipped']}"
            )
            
        except Exception as e:
            logger.error(f"Outbox flush operation failed: {e}")
            raise
        
        return stats
    
    async def _get_unprocessed_events(self) -> List[OutboxEvent]:
        """Get unprocessed outbox events ready for processing.
        
        Returns:
            List of unprocessed events.
        """
        # Calculate retry cutoff time
        retry_cutoff = timezone.now() - timedelta(minutes=self._retry_delay_minutes)
        
        # Query for unprocessed events
        events = OutboxEvent.objects.filter(
            processed_at__isnull=True
        ).filter(
            # Include events that haven't been attempted yet
            # or events that can be retried (past retry delay and under max retries)
            models.Q(attempts=0) |
            models.Q(
                attempts__lt=self._max_retries,
                created_at__lt=retry_cutoff
            )
        ).order_by('created_at')[:self._batch_size * 2]  # Get extra for buffering
        
        return [event async for event in events]
    
    async def _process_batch(self, events: List[OutboxEvent]) -> Dict[str, int]:
        """Process a batch of outbox events.
        
        Args:
            events: Batch of events to process.
            
        Returns:
            Processing statistics for the batch.
        """
        stats = {'processed': 0, 'failed': 0, 'skipped': 0}
        
        for event in events:
            try:
                result = await self._process_event(event)
                stats[result] += 1
            except Exception as e:
                logger.error(f"Error processing event {event.id}: {e}")
                stats['failed'] += 1
        
        return stats
    
    async def _process_event(self, event: OutboxEvent) -> str:
        """Process a single outbox event.
        
        Args:
            event: Outbox event to process.
            
        Returns:
            Processing result: 'processed', 'failed', or 'skipped'.
        """
        logger.debug(f"Processing outbox event: {event.id} ({event.event_type})")
        
        # Check if we have a handler for this event type
        handler = self._handlers.get(event.event_type)
        if not handler:
            logger.debug(f"No handler for event type: {event.event_type}")
            return 'skipped'
        
        # Check if event has exceeded max retries
        if event.attempts >= self._max_retries:
            logger.warning(
                f"Event {event.id} exceeded max retries ({self._max_retries})"
            )
            return 'skipped'
        
        try:
            # Process the event
            await handler.handle(event.event_type, event.payload)
            
            # Mark as processed
            async with transaction.atomic():
                event.mark_processed()
                await event.asave()
            
            logger.debug(f"Successfully processed event: {event.id}")
            return 'processed'
            
        except Exception as e:
            logger.error(f"Failed to process event {event.id}: {e}")
            
            # Increment attempts and record error
            async with transaction.atomic():
                event.increment_attempts(str(e))
                await event.asave()
            
            return 'failed'
    
    async def retry_failed_events(self) -> Dict[str, int]:
        """Retry events that have failed but are under the retry limit.
        
        Returns:
            Processing statistics for retry operation.
        """
        logger.info("Starting failed events retry operation")
        
        # Get failed events that can be retried
        retry_cutoff = timezone.now() - timedelta(minutes=self._retry_delay_minutes)
        
        failed_events = OutboxEvent.objects.filter(
            processed_at__isnull=True,
            attempts__gt=0,
            attempts__lt=self._max_retries,
            created_at__lt=retry_cutoff
        ).order_by('created_at')[:self._batch_size]
        
        events_list = [event async for event in failed_events]
        
        if not events_list:
            logger.debug("No failed events ready for retry")
            return {'processed': 0, 'failed': 0, 'skipped': 0}
        
        logger.info(f"Retrying {len(events_list)} failed events")
        return await self._process_batch(events_list)
    
    async def cleanup_processed_events(self, older_than_days: int = 30) -> int:
        """Clean up old processed events.
        
        Args:
            older_than_days: Remove processed events older than this many days.
            
        Returns:
            Number of events deleted.
        """
        logger.info(f"Cleaning up processed events older than {older_than_days} days")
        
        cutoff_date = timezone.now() - timedelta(days=older_than_days)
        
        deleted_count, _ = await OutboxEvent.objects.filter(
            processed_at__isnull=False,
            processed_at__lt=cutoff_date
        ).adelete()
        
        logger.info(f"Cleaned up {deleted_count} processed events")
        return deleted_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get outbox statistics.
        
        Returns:
            Dictionary with outbox statistics.
        """
        return {
            'total_events': OutboxEvent.objects.count(),
            'processed_events': OutboxEvent.objects.filter(processed_at__isnull=False).count(),
            'pending_events': OutboxEvent.objects.filter(processed_at__isnull=True).count(),
            'failed_events': OutboxEvent.objects.filter(
                processed_at__isnull=True,
                attempts__gt=0
            ).count(),
            'registered_handlers': list(self._handlers.keys()),
            'max_retries': self._max_retries,
            'retry_delay_minutes': self._retry_delay_minutes,
            'batch_size': self._batch_size,
        }


# Factory function for dependency injection
def create_outbox_dispatcher(
    max_retries: int = 3,
    retry_delay_minutes: int = 5,
    batch_size: int = 50
) -> OutboxDispatcher:
    """Create an outbox dispatcher with specified configuration.
    
    Args:
        max_retries: Maximum retry attempts per event.
        retry_delay_minutes: Delay between retries.
        batch_size: Events per processing batch.
        
    Returns:
        Configured outbox dispatcher instance.
    """
    return OutboxDispatcher(
        max_retries=max_retries,
        retry_delay_minutes=retry_delay_minutes,
        batch_size=batch_size
    )