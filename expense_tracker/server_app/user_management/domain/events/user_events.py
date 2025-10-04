"""User management domain events.

This module contains all domain events related to user operations.
Domain events represent significant business occurrences that may
be of interest to other bounded contexts or for audit purposes.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..value_objects.user_id import UserId
from ..value_objects.email import Email
from ..value_objects.first_name import FirstName
from ..value_objects.last_name import LastName


@dataclass(frozen=True, slots=True)
class DomainEvent(ABC):
    """Base class for all domain events.
    
    This abstract base class defines the common structure and behavior
    for all domain events in the user management context.
    """
    
    aggregate_id: UserId
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())
    event_version: int = field(default=1)
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the type identifier for this event."""
        pass
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a dictionary representation.
        
        Returns:
            Dictionary representation of the event.
        """
        return {
            'event_id': str(self.event_id),
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': str(self.aggregate_id),
            'event_version': self.event_version,
            'data': self._get_event_data()
        }
    
    @abstractmethod
    def _get_event_data(self) -> dict[str, Any]:
        """Get the event-specific data.
        
        Returns:
            Dictionary containing event-specific data.
        """
        pass







@dataclass(frozen=True, slots=True)
class UserRegistered:
    """Event raised when a new user is registered.
    
    This event is published when a user successfully completes registration
    and their account is created in the system.
    """
    
    aggregate_id: UserId
    email: Email
    first_name: FirstName
    last_name: LastName
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())
    event_version: int = field(default=1)
    
    @property
    def event_type(self) -> str:
        return "user_registered"
    
    def _get_event_data(self) -> dict[str, Any]:
        return {
            'email': str(self.email),
            'first_name': str(self.first_name),
            'last_name': str(self.last_name),
            'full_name': f"{self.first_name} {self.last_name}"
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a dictionary representation."""
        return {
            'event_id': str(self.event_id),
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': str(self.aggregate_id),
            'event_version': self.event_version,
            'data': self._get_event_data()
        }







@dataclass(frozen=True, slots=True)
class UserPasswordChanged:
    """Event raised when a user changes their password.
    
    This event is published when a user successfully changes their password.
    For security reasons, no password information is included in the event.
    """
    
    aggregate_id: UserId
    email: Email
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())
    event_version: int = field(default=1)
    
    @property
    def event_type(self) -> str:
        return "user_password_changed"
    
    def _get_event_data(self) -> dict[str, Any]:
        return {
            'email': str(self.email)
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a dictionary representation."""
        return {
            'event_id': str(self.event_id),
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': str(self.aggregate_id),
            'event_version': self.event_version,
            'data': self._get_event_data()
        }







@dataclass(frozen=True, slots=True)
class UserDeactivated:
    """Event raised when a user account is deactivated.
    
    This event is published when a user account is deactivated,
    either by the user themselves or by an administrator.
    """
    
    aggregate_id: UserId
    email: Email
    reason: Optional[str] = None
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())
    event_version: int = field(default=1)
    
    @property
    def event_type(self) -> str:
        return "user_deactivated"
    
    def _get_event_data(self) -> dict[str, Any]:
        return {
            'email': str(self.email),
            'reason': self.reason
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a dictionary representation."""
        return {
            'event_id': str(self.event_id),
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': str(self.aggregate_id),
            'event_version': self.event_version,
            'data': self._get_event_data()
        }







@dataclass(frozen=True, slots=True)
class UserProfileUpdated:
    """Event raised when a user updates their profile information.
    
    This event is published when a user successfully updates their
    profile information such as name or email.
    """
    
    aggregate_id: UserId
    old_email: Optional[Email]
    new_email: Optional[Email] 
    old_first_name: Optional[FirstName]
    new_first_name: Optional[FirstName]
    old_last_name: Optional[LastName]
    new_last_name: Optional[LastName]
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())
    event_version: int = field(default=1)
    
    @property
    def event_type(self) -> str:
        return "user_profile_updated"
    
    def _get_event_data(self) -> dict[str, Any]:
        return {
            'old_email': str(self.old_email) if self.old_email else None,
            'new_email': str(self.new_email) if self.new_email else None,
            'old_first_name': str(self.old_first_name) if self.old_first_name else None,
            'new_first_name': str(self.new_first_name) if self.new_first_name else None,
            'old_last_name': str(self.old_last_name) if self.old_last_name else None,
            'new_last_name': str(self.new_last_name) if self.new_last_name else None,
            'old_full_name': f"{self.old_first_name} {self.old_last_name}" if self.old_first_name and self.old_last_name else None,
            'new_full_name': f"{self.new_first_name} {self.new_last_name}" if self.new_first_name and self.new_last_name else None
        }
    
    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a dictionary representation."""
        return {
            'event_id': str(self.event_id),
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'aggregate_id': str(self.aggregate_id),
            'event_version': self.event_version,
            'data': self._get_event_data()
        }