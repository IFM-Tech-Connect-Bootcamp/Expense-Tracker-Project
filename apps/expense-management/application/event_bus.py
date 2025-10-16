"""In-process event bus for the application layer.

This module provides an event bus implementation for dispatching
domain events within the modular monolith architecture.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, TypeVar

from ..domain.events.expense_events import DomainEvent


T = TypeVar('T', bound=DomainEvent)
EventHandler = Callable[[T], None]

logger = logging.getLogger(__name__)


class EventBus:
    """In-process event bus for domain event dispatching.
    
    This event bus handles the publication and subscription of domain events
    within the application layer. It supports multiple subscribers per event type
    and provides error handling for failed subscriptions.
    """
    
    def __init__(self) -> None:
        """Initialize the event bus."""
        self._subscribers: Dict[Type[DomainEvent], List[EventHandler]] = defaultdict(list)
        self._event_count = 0
    
    def subscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Subscribe a handler to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to.
            handler: The handler function to call when the event is published.
        """
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed handler {handler.__name__} to {event_type.__name__}")
    
    def unsubscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Unsubscribe a handler from a specific event type.
        
        Args:
            event_type: The type of event to unsubscribe from.
            handler: The handler function to remove.
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed handler {handler.__name__} from {event_type.__name__}")
            except ValueError:
                logger.warning(f"Handler {handler.__name__} was not subscribed to {event_type.__name__}")
    
    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribed handlers.
        
        Args:
            event: The domain event to publish.
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        
        self._event_count += 1
        logger.debug(f"Publishing event {event_type.__name__} (#{self._event_count}) to {len(handlers)} handlers")
        
        for handler in handlers:
            try:
                handler(event)
                logger.debug(f"Successfully handled event {event_type.__name__} with {handler.__name__}")
            except Exception as e:
                logger.error(
                    f"Error handling event {event_type.__name__} with {handler.__name__}: {e}",
                    exc_info=True
                )
                # Continue with other handlers even if one fails
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """Publish multiple events in order.
        
        Args:
            events: A list of domain events to publish in sequence.
        """
        for event in events:
            self.publish(event)