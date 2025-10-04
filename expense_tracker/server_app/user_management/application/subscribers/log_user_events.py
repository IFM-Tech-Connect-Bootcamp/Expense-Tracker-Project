"""Log user events subscriber.

This module contains the subscriber for logging all user-related
domain events for audit purposes.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def log_user_events(event: Any) -> None:
    """Log user domain events for audit purposes.
    
    This subscriber handles all user domain events by creating
    structured audit log entries with comprehensive event metadata.
    
    Args:
        event: Any user domain event.
    """
    try:
        event_data = {
            'event_type': event.event_type,
            'event_id': str(event.event_id),
            'aggregate_id': str(event.aggregate_id),
            'occurred_at': event.occurred_at.isoformat(),
            'event_version': event.event_version
        }
        
        # Add event-specific data if available
        if hasattr(event, '_get_event_data'):
            event_data['data'] = event._get_event_data()
        
        logger.info(
            f"User event logged: {event.event_type}",
            extra={
                'event_data': event_data,
                'user_id': str(event.aggregate_id),
                'event_type': event.event_type
            }
        )
        
        # TODO: In a real implementation, this could:
        # - Store events in an audit log database
        # - Send events to external audit systems
        # - Trigger alerting for sensitive operations
        # - Generate compliance reports
        
    except Exception as e:
        logger.error(
            f"Failed to log user event {getattr(event, 'event_type', 'unknown')}: {e}",
            exc_info=True
        )
        # Don't re-raise - logging failure shouldn't break the operation