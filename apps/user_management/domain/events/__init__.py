"""Domain events for User Management.

This package contains all domain events that can be raised during
user management operations. These events represent significant
business occurrences that other bounded contexts may be interested in.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = ["DomainEvent", "UserRegistered", "UserPasswordChanged", "UserDeactivated", "UserProfileUpdated"]