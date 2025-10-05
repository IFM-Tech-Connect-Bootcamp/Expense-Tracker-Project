"""Change password handler."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from ...domain.errors import UserManagementDomainError
from ...domain.events.user_events import DomainEvent
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.password_hash import PasswordHash
from ...domain.value_objects.user_id import UserId
from ..commands.change_password import ChangePasswordCommand
from ..errors import translate_domain_error

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class PasswordService(Protocol):
    """Protocol for password service operations."""
    
    async def hash_password(self, password: str) -> str:
        """Hash a password."""
        ...
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        ...


@dataclass(frozen=True)
class ChangePasswordResult:
    """Result of password change operation."""
    events: list[DomainEvent]


class ChangePasswordHandler:
    """Handler for password change operations.
    
    This handler orchestrates the password change use case by:
    1. Validating the password change request
    2. Finding the user by ID
    3. Verifying the current password
    4. Checking user status and permissions
    5. Hashing the new password
    6. Updating the user entity
    7. Publishing domain events
    8. Returning the operation result
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        """Initialize the change password handler.
        
        Args:
            user_repository: Repository for user persistence operations.
            password_service: Service for password hashing and verification operations.
        """
        self._user_repository = user_repository
        self._password_service = password_service
    
    async def handle(self, command: ChangePasswordCommand) -> ChangePasswordResult:
        """Execute the password change use case.
        
        Args:
            command: The password change command containing user credentials.
            
        Returns:
            ChangePasswordResult containing domain events.
            
        Raises:
            UserNotFoundError: If the user doesn't exist.
            InvalidCredentialsError: If the old password is incorrect.
            InvalidOperationError: If the user is not active.
        """
        logger.info(f"Executing password change for user ID: {command.user_id}")
        
        try:
            # Step 1: Validate the password change request
            logger.debug(f"Validating password change request for user: {command.user_id}")
            user_id = UserId.from_string(command.user_id)
            
            # Step 2: Find user by ID
            logger.debug(f"Finding user by ID: {command.user_id}")
            user = await self._user_repository.find_by_id(user_id)
            if user is None:
                logger.warning(f"Password change failed: User not found: {command.user_id}")
                from ...domain.errors import UserNotFoundError
                raise UserNotFoundError(user_id.value)
            
            # Step 3: Verify current password
            logger.debug(f"Verifying current password for user: {command.user_id}")
            current_hash = user.password_hash.value if hasattr(user.password_hash, 'value') else user.password_hash
            is_valid = await self._password_service.verify_password(
                command.old_password,
                current_hash
            )
            if not is_valid:
                logger.warning(f"Password change failed: Invalid old password for user: {command.user_id}")
                from ...domain.errors import InvalidCredentialsError
                raise InvalidCredentialsError(user.email.value)
            
            # Step 4: Check if user is active (business rule)
            logger.debug(f"Checking user status for password change: {command.user_id}")
            if not user.is_active():
                logger.warning(f"Password change failed: User is inactive: {command.user_id}")
                from ...domain.errors import InvalidOperationError
                raise InvalidOperationError(
                    "change_password",
                    "Cannot change password for an inactive user"
                )
            
            # Step 5: Hash new password and update
            logger.debug(f"Hashing new password for user: {command.user_id}")
            new_password_hash = await self._password_service.hash_password(command.new_password)
            user.password_hash = PasswordHash(new_password_hash)
            
            # Step 6: Update user entity with timestamp
            from datetime import datetime
            user.updated_at = datetime.utcnow()
            
            # Step 7: Manually trigger the password changed event
            logger.debug(f"Creating password changed event for user: {command.user_id}")
            from ...domain.events.user_events import UserPasswordChanged
            
            password_changed_event = UserPasswordChanged(
                aggregate_id=user.id,
                email=user.email
            )
            user._add_domain_event(password_changed_event)
            
            # Step 8: Persist the updated user
            logger.debug(f"Persisting updated user: {command.user_id}")
            await self._user_repository.save(user)
            
            # Step 9: Collect domain events for publishing
            events = user.get_domain_events()
            user.clear_domain_events()
            logger.info(f"Password successfully changed for user: {command.user_id}, collected {len(events)} domain events")
            
            return ChangePasswordResult(events=events)
            
        except UserManagementDomainError as e:
            logger.error(f"Domain error during password change for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during password change for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e