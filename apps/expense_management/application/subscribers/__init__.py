"""Subscribers package for Expense Management application layer.

This package contains event subscribers that handle domain events
for audit logging, monitoring, and other side effects.
"""

from .log_expense_events import log_expense_events

__all__ = [
    "log_expense_events",
]