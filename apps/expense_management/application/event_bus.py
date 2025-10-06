"""In-process event bus for the expense management application layer.

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
            events: List of domain events to publish.
        """
        for event in events:
            self.publish(event)
    
    def get_subscriber_count(self, event_type: Type[DomainEvent]) -> int:
        """Get the number of subscribers for a specific event type.
        
        Args:
            event_type: The event type to check.
            
        Returns:
            Number of subscribers for the event type.
        """
        return len(self._subscribers.get(event_type, []))
    
    def get_total_subscribers(self) -> int:
        """Get the total number of subscribed handlers across all event types.
        
        Returns:
            Total number of subscribed handlers.
        """
        return sum(len(handlers) for handlers in self._subscribers.values())
    
    def get_event_types(self) -> List[Type[DomainEvent]]:
        """Get all event types that have subscribers.
        
        Returns:
            List of event types with subscribers.
        """
        return list(self._subscribers.keys())
    
    def clear_subscribers(self, event_type: Type[DomainEvent] = None) -> None:
        """Clear subscribers for a specific event type or all event types.
        
        Args:
            event_type: Specific event type to clear. If None, clears all.
        """
        if event_type:
            if event_type in self._subscribers:
                del self._subscribers[event_type]
                logger.debug(f"Cleared all subscribers for {event_type.__name__}")
        else:
            self._subscribers.clear()
            logger.debug("Cleared all subscribers for all event types")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics.
        
        Returns:
            Dictionary containing event bus statistics.
        """
        return {
            'total_event_types': len(self._subscribers),
            'total_subscribers': self.get_total_subscribers(),
            'events_published': self._event_count,
            'event_types': [event_type.__name__ for event_type in self._subscribers.keys()]
        }
    
    def __str__(self) -> str:
        """Return string representation."""
        stats = self.get_statistics()
        return (
            f"EventBus(event_types={stats['total_event_types']}, "
            f"subscribers={stats['total_subscribers']}, "
            f"published={stats['events_published']})"
        )


# Global event bus instance for the application
event_bus = EventBus()