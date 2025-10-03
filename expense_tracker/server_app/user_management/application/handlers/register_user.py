"""Register user handler.

This module contains the handler for user registration use cases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from ...domain.entities.user import User
from ...domain.errors import UserManagementDomainError
from ...domain.events.user_events import DomainEvent, UserRegistered
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...domain.value_objects.first_name import FirstName
from ...domain.value_objects.last_name import LastName
from ...domain.value_objects.password_hash import PasswordHash
from ...domain.value_objects.user_id import UserId
from ..commands.register_user import RegisterUserCommand
from ..errors import ApplicationError
from ..dto import UserDTO
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
class RegisterUserResult:
    """Result of user registration operation."""
    user_dto: UserDTO
    events: list[DomainEvent]


class RegisterUserHandler:
    """Handler for user registration operations.
    
    This handler orchestrates the user registration use case by:
    1. Validating the registration request
    2. Checking for existing users with the same email
    3. Creating a new user domain entity
    4. Persisting the user through the repository
    5. Publishing domain events for downstream processing
    6. Returning a user DTO response
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        """Initialize the register user handler.
        
        Args:
            user_repository: Repository for user persistence operations.
            password_service: Service for password hashing operations.
        """
        self._user_repository = user_repository
        self._password_service = password_service
    
    async def handle(self, command: RegisterUserCommand) -> RegisterUserResult:
        """Execute the user registration use case.
        
        Args:
            command: The registration command containing user data.
            
        Returns:
            RegisterUserResult containing user DTO and domain events.
            
        Raises:
            ApplicationError: If registration fails for any reason.
        """
        logger.info(f"Executing user registration for email: {command.email}")
        
        try:
            # Step 1: Validate the registration request
            logger.debug(f"Validating registration request for email: {command.email}")
            
            # Create domain value objects
            email = Email(command.email)
            first_name = FirstName(command.first_name)
            last_name = LastName(command.last_name)
            
            # Step 2: Check if user already exists
            logger.debug(f"Checking if user with email {command.email} already exists")
            existing_user = await self._user_repository.find_by_email(email)
            if existing_user is not None:
                logger.warning(f"Registration failed: User with email {command.email} already exists")
                from ...domain.errors import UserAlreadyExistsError
                raise UserAlreadyExistsError(email.value)
            
            # Step 3: Hash the password
            logger.debug("Hashing user password for secure storage")
            hashed_password = await self._password_service.hash_password(command.password)
            password_hash = PasswordHash(hashed_password)
            
            # Step 4: Create new user domain entity
            logger.debug(f"Creating new user entity for {command.email}")
            user = User.create(
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                user_id=UserId.new()
            )
            
            # Step 5: Persist the user
            logger.debug(f"Persisting user {user.id} to repository")
            await self._user_repository.save(user)
            
            # Step 6: Create user DTO for response
            logger.debug(f"Creating user DTO for successful registration of {command.email}")
            user_dto = UserDTO(
                id=str(user.id.value),
                email=user.email.value,
                first_name=user.first_name.value,
                last_name=user.last_name.value,
                full_name=f"{user.first_name.value} {user.last_name.value}",
                status=user.status.value,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            # Step 7: Collect domain events for publishing
            events = user.get_domain_events()
            user.clear_domain_events()
            logger.info(f"User registration completed successfully for {command.email}, collected {len(events)} domain events")
            
            return RegisterUserResult(
                user_dto=user_dto,
                events=events
            )
            
        except UserManagementDomainError as e:
            logger.error(f"Domain error during user registration for {command.email}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during user registration for {command.email}: {str(e)}")
            raise ApplicationError(f"Failed to register user: {str(e)}") from e