"""Deactivate user handler."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...domain.errors import UserManagementDomainError
from ...domain.events.user_events import DomainEvent
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_id import UserId
from ..commands.deactivate_user import DeactivateUserCommand
from ..errors import translate_domain_error

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeactivateUserResult:
    """Result of user deactivation operation."""
    events: list[DomainEvent]


class DeactivateUserHandler:
    """Handler for user deactivation operations.
    
    This handler orchestrates the user deactivation use case by:
    1. Validating the deactivation request
    2. Finding the user by ID
    3. Deactivating the user account with reason
    4. Persisting the updated user
    5. Publishing domain events
    6. Returning the operation result
    """
    
    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the deactivate user handler.
        
        Args:
            user_repository: Repository for user persistence operations.
        """
        self._user_repository = user_repository
    
    async def handle(self, command: DeactivateUserCommand) -> DeactivateUserResult:
        """Execute the user deactivation use case.
        
        Args:
            command: The deactivation command containing user ID and reason.
            
        Returns:
            DeactivateUserResult containing domain events.
            
        Raises:
            UserNotFoundError: If the user doesn't exist.
        """
        logger.info(f"Executing user deactivation for user ID: {command.user_id}")
        
        try:
            # Step 1: Validate the deactivation request
            logger.debug(f"Validating deactivation request for user: {command.user_id}")
            user_id = UserId.from_string(command.user_id)
            
            # Step 2: Find user by ID
            logger.debug(f"Finding user by ID: {command.user_id}")
            user = await self._user_repository.find_by_id(user_id)
            if user is None:
                logger.warning(f"Deactivation failed: User not found: {command.user_id}")
                from ...domain.errors import UserNotFoundError
                raise UserNotFoundError(user_id.value)
            
            # Step 3: Deactivate user account (domain method handles business rules)
            logger.debug(f"Deactivating user account for user: {command.user_id}, reason: {command.reason}")
            user.deactivate(reason=command.reason)
            
            # Step 4: Persist the updated user
            logger.debug(f"Persisting deactivated user: {command.user_id}")
            await self._user_repository.update(user)
            
            # Step 5: Collect domain events for publishing
            events = user.get_domain_events()
            user.clear_domain_events()
            logger.info(f"User successfully deactivated: {command.user_id}, collected {len(events)} domain events")
            
            return DeactivateUserResult(events=events)
            
        except UserManagementDomainError as e:
            logger.error(f"Domain error during user deactivation for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during user deactivation for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e