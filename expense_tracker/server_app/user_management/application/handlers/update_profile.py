"""Update profile handler."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ...domain.errors import UserManagementDomainError
from ...domain.events.user_events import DomainEvent
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.first_name import FirstName
from ...domain.value_objects.last_name import LastName
from ...domain.value_objects.user_id import UserId
from ..commands.update_profile import UpdateProfileCommand
from ..dtos import UserDTO
from ..errors import translate_domain_error

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateProfileResult:
    """Result of profile update operation."""
    user_dto: UserDTO
    events: list[DomainEvent]


class UpdateProfileHandler:
    """Handler for user profile update operations.
    
    This handler orchestrates the profile update use case by:
    1. Validating the profile update request
    2. Finding the user by ID
    3. Updating the user's profile information (name components)
    4. Persisting the updated user
    5. Publishing domain events
    6. Returning the updated user DTO
    """
    
    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the update profile handler.
        
        Args:
            user_repository: Repository for user persistence operations.
        """
        self._user_repository = user_repository
    
    async def handle(self, command: UpdateProfileCommand) -> UpdateProfileResult:
        """Execute the profile update use case.
        
        Args:
            command: The profile update command containing new profile data.
            
        Returns:
            UpdateProfileResult containing updated user DTO and domain events.
            
        Raises:
            UserNotFoundError: If the user doesn't exist.
        """
        logger.info(f"Executing profile update for user ID: {command.user_id}")
        
        try:
            # Step 1: Validate the profile update request
            logger.debug(f"Validating profile update request for user: {command.user_id}")
            user_id = UserId.from_string(command.user_id)
            
            # Step 2: Find user by ID
            logger.debug(f"Finding user by ID: {command.user_id}")
            user = await self._user_repository.find_by_id(user_id)
            if user is None:
                logger.warning(f"Profile update failed: User not found: {command.user_id}")
                from ...domain.errors import UserNotFoundError
                raise UserNotFoundError(user_id.value)
            
            # Step 3: Prepare profile update values
            logger.debug(f"Preparing profile update values for user: {command.user_id}")
            new_first_name = FirstName(command.new_first_name) if command.new_first_name else None
            new_last_name = LastName(command.new_last_name) if command.new_last_name else None
            
            # Step 4: Update user profile (domain method handles validation)
            logger.debug(f"Updating user profile for user: {command.user_id}")
            user.update_profile(
                new_first_name=new_first_name, 
                new_last_name=new_last_name
            )
            
            # Step 5: Persist the updated user
            logger.debug(f"Persisting updated user: {command.user_id}")
            await self._user_repository.save(user)
            
            # Step 6: Create user DTO for response
            logger.debug(f"Creating user DTO for successful profile update of user: {command.user_id}")
            user_dto = UserDTO(
                id=str(user.id.value),
                email=user.email.value,
                first_name=user.first_name.value,
                last_name=user.last_name.value,
                status=user.status.value,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            # Step 7: Collect domain events for publishing
            events = user.get_domain_events()
            user.clear_domain_events()
            logger.info(f"Profile successfully updated for user: {command.user_id}, collected {len(events)} domain events")
            
            return UpdateProfileResult(user_dto=user_dto, events=events)
            
        except UserManagementDomainError as e:
            logger.error(f"Domain error during profile update for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during profile update for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e