"""Log expense events subscriber.

This module contains the subscriber for logging all expense-related
domain events for audit purposes.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def log_expense_events(event: Any) -> None:
    """Log expense domain events for audit purposes.
    
    This subscriber handles all expense and category domain events by creating
    structured audit log entries with comprehensive event metadata.
    
    Args:
        event: Any expense or category domain event.
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
            f"Expense event logged: {event.event_type}",
            extra={
                'event_data': event_data,
                'aggregate_id': str(event.aggregate_id),
                'event_type': event.event_type
            }
        )
        
        # TODO: In a real implementation, this could:
        # - Store events in an audit log database for financial compliance
        # - Send events to external financial audit systems
        # - Trigger alerting for large expense amounts
        # - Generate expense reports for tax purposes
        # - Integrate with accounting systems
        # - Track spending patterns for analytics
        # - Monitor for suspicious expense patterns
        
    except Exception as e:
        logger.error(
            f"Failed to log expense event {getattr(event, 'event_type', 'unknown')}: {e}",
            exc_info=True
        )
        # Don't re-raise - logging failure shouldn't break the operation