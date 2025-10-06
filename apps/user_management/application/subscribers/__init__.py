"""Subscribers package for handling domain events.

This package contains event subscribers that handle domain events
and trigger side effects in response to business actions.
"""

from .log_user_events import log_user_events

__all__ = [
    "log_user_events",
]