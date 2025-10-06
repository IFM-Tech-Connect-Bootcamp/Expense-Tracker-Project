"""Infrastructure subscribers package.

This package contains event subscribers that handle domain events
and forward them to external systems via the outbox pattern.
"""

from .notify_on_user_events import (
    on_user_deactivated,
    on_user_password_changed,
    on_user_profile_updated,
    on_user_registered,
)

__all__ = [
    "on_user_registered",
    "on_user_password_changed", 
    "on_user_profile_updated",
    "on_user_deactivated",
]