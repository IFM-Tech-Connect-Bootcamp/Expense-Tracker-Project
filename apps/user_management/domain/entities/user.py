"""User entity - the aggregate root for user management.

This module contains the User entity which serves as the aggregate root
for the user management bounded context. It encapsulates all user-related
business logic and invariants.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from django.utils import timezone

from ..value_objects.user_id import UserId
from ..value_objects.email import Email
from ..value_objects.password_hash import PasswordHash
from ..value_objects.first_name import FirstName
from ..value_objects.last_name import LastName
from ..enums.user_status import UserStatus
from ..errors import (
    InvalidOperationError,
    DomainValidationError,
    PasswordPolicyError
)

if TYPE_CHECKING:
    from ..services.password_policy import PasswordHasher
    from ..events.user_events import DomainEvent


@dataclass
class User:
    """User aggregate root entity.
    
    This entity represents a user in the system and serves as the aggregate root
    for the user management bounded context. It encapsulates all user-related
    business logic, invariants, and state transitions.
    
    The User entity is responsible for:
    - Maintaining user identity and profile information
    - Managing password changes and validation
    - Controlling user status and lifecycle
    - Ensuring business rule compliance
    - Publishing domain events for significant state changes
    """
    
    id: UserId
    email: Email
    password_hash: PasswordHash
    first_name: FirstName
    last_name: LastName
    created_at: datetime = field(default_factory=timezone.now)
    updated_at: datetime = field(default_factory=lambda: timezone.now())
    status: UserStatus = UserStatus.ACTIVE
    
    # Domain events that occurred during this session
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False)
    
    def __post_init__(self) -> None:
        """Validate the user entity after initialization."""
        self._validate_invariants()
    
    def _validate_invariants(self) -> None:
        """Validate business invariants for the user entity.
        
        Raises:
            DomainValidationError: If any invariants are violated.
        """
        # Names are now required and validated by their value objects
        # No additional validation needed here for names
        
        if self.created_at > timezone.now():
            raise DomainValidationError("User", "Created date cannot be in the future")
        
        if self.updated_at < self.created_at:
            raise DomainValidationError("User", "Updated date cannot be before created date")
    
    


    
    
    @classmethod
    def create(
        cls,
        email: Email,
        password_hash: PasswordHash,
        first_name: FirstName,
        last_name: LastName,
        user_id: Optional[UserId] = None
    ) -> User:
        """Create a new user instance.
        
        This factory method creates a new user with proper initialization
        and publishes the appropriate domain event.
        
        Args:
            email: The user's email address.
            password_hash: The hashed password.
            first_name: The user's first name.
            last_name: The user's last name.
            user_id: Optional specific user ID (defaults to new UUID).
            
        Returns:
            A new User instance.
            
        Raises:
            DomainValidationError: If the user data is invalid.
        """
        user_id = user_id or UserId.new()
        now = timezone.now()
        
        user = cls(
            id=user_id,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            created_at=now,
            updated_at=now,
            status=UserStatus.ACTIVE
        )
        
        # Import here to avoid circular dependencies
        from ..events.user_events import UserRegistered
        
        user._add_domain_event(UserRegistered(
            aggregate_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        ))
        
        return user
    
    
    
    


    def update_profile(
        self, 
        new_email: Optional[Email] = None, 
        new_first_name: Optional[FirstName] = None,
        new_last_name: Optional[LastName] = None
    ) -> None:
        """Update the user's profile information.
        
        Args:
            new_email: New email address (optional).
            new_first_name: New first name (optional).
            new_last_name: New last name (optional).
            
        Raises:
            InvalidOperationError: If the user is not active.
            DomainValidationError: If the new data is invalid.
        """
        if not self.is_active():
            raise InvalidOperationError(
                "update_profile",
                "Cannot update profile of an inactive user"
            )
        
        old_email = self.email
        old_first_name = self.first_name
        old_last_name = self.last_name
        
        # Update fields if provided
        if new_email is not None:
            self.email = new_email
        
        if new_first_name is not None:
            self.first_name = new_first_name
            
        if new_last_name is not None:
            self.last_name = new_last_name
        
        # Update timestamp
        self.updated_at = timezone.now()
        
        # Validate after updates
        self._validate_invariants()
        
        # Publish event if anything changed
        if (new_email != old_email or 
            new_first_name != old_first_name or 
            new_last_name != old_last_name):
            from ..events.user_events import UserProfileUpdated
            
            self._add_domain_event(UserProfileUpdated(
                aggregate_id=self.id,
                old_email=old_email,
                new_email=new_email if new_email != old_email else None,
                old_first_name=old_first_name,
                new_first_name=new_first_name if new_first_name != old_first_name else None,
                old_last_name=old_last_name,
                new_last_name=new_last_name if new_last_name != old_last_name else None
            ))
    
    


    
    
    
    async def verify_password(self, plain_password: str, password_hasher: PasswordHasher) -> bool:
        """Verify a plain text password against the stored hash.
        
        Args:
            plain_password: The plain text password to verify.
            password_hasher: Service for password verification.
            
        Returns:
            True if the password matches, False otherwise.
            
        Raises:
            InvalidOperationError: If the user is not active.
        """
        if not self.is_active():
            raise InvalidOperationError(
                "verify_password",
                "Cannot verify password for an inactive user"
            )
        
        return await password_hasher.verify(self.password_hash, plain_password)
    
    
    
    
    
    
    async def change_password(
        self, 
        old_password: str, 
        new_password: str, 
        password_hasher: PasswordHasher
    ) -> None:
        """Change the user's password.
        
        Args:
            old_password: Current password for verification.
            new_password: New plain text password.
            password_hasher: Service for password operations.
            
        Raises:
            InvalidOperationError: If the user is not active or old password is wrong.
            PasswordPolicyError: If the new password doesn't meet policy requirements.
        """
        if not self.is_active():
            raise InvalidOperationError(
                "change_password",
                "Cannot change password for an inactive user"
            )
        
        # Verify old password
        if not await password_hasher.verify(self.password_hash, old_password):
            raise InvalidOperationError(
                "change_password",
                "Current password is incorrect"
            )
        
        # Hash the new password (this will validate policy via the hasher)
        self.password_hash = await password_hasher.hash(new_password)
        self.updated_at = timezone.now()
        
        # Publish event
        from ..events.user_events import UserPasswordChanged
        
        self._add_domain_event(UserPasswordChanged(
            aggregate_id=self.id,
            email=self.email
        ))
    
    
    
    
    
    
    def deactivate(self, reason: Optional[str] = None) -> None:
        """Deactivate the user account.
        
        Args:
            reason: Optional reason for deactivation.
            
        Raises:
            InvalidOperationError: If the user is already inactive.
        """
        if not self.is_active():
            raise InvalidOperationError(
                "deactivate",
                "User is already deactivated"
            )
        
        self.status = UserStatus.DEACTIVATED
        self.updated_at = timezone.now()
        
        # Publish event
        from ..events.user_events import UserDeactivated
        
        self._add_domain_event(UserDeactivated(
            aggregate_id=self.id,
            email=self.email,
            reason=reason
        ))
    
    
    
    
    
    
    def reactivate(self) -> None:
        """Reactivate a deactivated user account.
        
        Raises:
            InvalidOperationError: If the user is already active.
        """
        if self.is_active():
            raise InvalidOperationError(
                "reactivate",
                "User is already active"
            )
        
        self.status = UserStatus.ACTIVE
        self.updated_at = timezone.now()
    
    
    
    
    
    def is_active(self) -> bool:
        """Check if the user is active.
        
        Returns:
            True if the user is active, False otherwise.
        """
        return self.status.is_active
    
    
    
    
    
    
    def is_deactivated(self) -> bool:
        """Check if the user is deactivated.
        
        Returns:
            True if the user is deactivated, False otherwise.
        """
        return self.status.is_deactivated
    
    
    
    
    
    
    def can_authenticate(self) -> bool:
        """Check if the user can authenticate.
        
        Returns:
            True if the user can authenticate, False otherwise.
        """
        return self.is_active()
    
    
    
    
    
    
    def get_domain_events(self) -> list[DomainEvent]:
        """Get the list of domain events that occurred.
        
        Returns:
            List of domain events.
        """
        return self._domain_events.copy()
    
    
    
    
    
    
    def clear_domain_events(self) -> None:
        """Clear the domain events list.
        
        This should be called after events have been published.
        """
        self._domain_events.clear()
    
    
    
    
    
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to the events list.
        
        Args:
            event: The domain event to add.
        """
        self._domain_events.append(event)
    
    
    
    
    
    
    def get_full_name(self) -> str:
        """Get the user's full name.
        
        Returns:
            The user's full name as a string.
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_display_name(self) -> str:
        """Get the user's display name (same as full name).
        
        Returns:
            The user's display name.
        """
        return self.get_full_name()
    
    def __str__(self) -> str:
        """Return string representation of the user."""
        status_str = "active" if self.is_active() else "inactive"
        return f"User({self.email}, {self.get_full_name()}, {status_str})"
    
    
    
    
    
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"User(id={self.id}, email={self.email}, "
            f"first_name={self.first_name!r}, last_name={self.last_name!r}, status={self.status})"
        )