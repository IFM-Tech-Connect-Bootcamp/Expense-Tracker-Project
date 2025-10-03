"""Application layer service orchestration.

This module provides a high-level service that orchestrates
all user management use cases by wiring handlers with event bus.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from ..domain.repositories.user_repository import UserRepository
from .commands import (
    AuthenticateUserCommand,
    ChangePasswordCommand,
    DeactivateUserCommand,
    RegisterUserCommand,
    UpdateProfileCommand,
)
from .dtos import AuthResultDTO, UserDTO
from .errors import ApplicationError
from .event_bus import EventBus
from .handlers import (
    AuthenticateUserHandler,
    ChangePasswordHandler,
    DeactivateUserHandler,
    RegisterUserHandler,
    UpdateProfileHandler,
)
from .subscribers import log_user_events

if TYPE_CHECKING:
    from ..domain.events.user_events import DomainEvent


class PasswordService(Protocol):
    """Protocol for password service operations."""
    
    async def hash_password(self, password: str) -> str:
        """Hash a password."""
        ...
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        ...


logger = logging.getLogger(__name__)


class UserManagementService:
    """High-level service orchestrating user management use cases.
    
    This service wires together handlers, event bus, and subscribers
    to provide a clean interface for executing user management operations.
    """
    
    def __init__(
        self, 
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        """Initialize the user management service.
        
        Args:
            user_repository: Repository for user persistence.
            password_service: Service for password operations.
        """
        self._event_bus = EventBus()
        
        # Set up event subscribers
        self._setup_event_subscribers()
        
        # Initialize handlers
        self._register_handler = RegisterUserHandler(user_repository, password_service)
        self._authenticate_handler = AuthenticateUserHandler(user_repository, password_service)
        self._change_password_handler = ChangePasswordHandler(user_repository, password_service)
        self._update_profile_handler = UpdateProfileHandler(user_repository)
        self._deactivate_handler = DeactivateUserHandler(user_repository)
    
    def _setup_event_subscribers(self) -> None:
        """Set up event subscribers on the event bus."""
        from ..domain.events.user_events import (
            UserDeactivated,
            UserPasswordChanged,
            UserProfileUpdated,
            UserRegistered,
        )
        
        # Subscribe to all user events for logging
        self._event_bus.subscribe(UserRegistered, log_user_events)
        self._event_bus.subscribe(UserPasswordChanged, log_user_events)
        self._event_bus.subscribe(UserDeactivated, log_user_events)
        self._event_bus.subscribe(UserProfileUpdated, log_user_events)
    
    async def register_user(self, command: RegisterUserCommand) -> UserDTO:
        """Register a new user.
        
        Args:
            command: The registration command.
            
        Returns:
            DTO representing the registered user.
            
        Raises:
            ApplicationError: If registration fails.
        """
        try:
            result = await self._register_handler.handle(command)
            await self._publish_events(result.events)
            return result.user_dto
        except Exception as e:
            logger.error(f"Failed to register user: {e}", exc_info=True)
            if isinstance(e, ApplicationError):
                raise
            raise ApplicationError(f"Registration failed: {e}") from e
    
    async def authenticate_user(self, command: AuthenticateUserCommand) -> AuthResultDTO:
        """Authenticate a user.
        
        Args:
            command: The authentication command.
            
        Returns:
            Authentication result DTO.
            
        Raises:
            ApplicationError: If authentication fails.
        """
        try:
            return await self._authenticate_handler.handle(command)
        except Exception as e:
            logger.error(f"Failed to authenticate user: {e}", exc_info=True)
            if isinstance(e, ApplicationError):
                raise
            raise ApplicationError(f"Authentication failed: {e}") from e
    
    async def change_password(self, command: ChangePasswordCommand) -> None:
        """Change a user's password.
        
        Args:
            command: The change password command.
            
        Raises:
            ApplicationError: If password change fails.
        """
        try:
            result = await self._change_password_handler.handle(command)
            await self._publish_events(result.events)
        except Exception as e:
            logger.error(f"Failed to change password: {e}", exc_info=True)
            if isinstance(e, ApplicationError):
                raise
            raise ApplicationError(f"Password change failed: {e}") from e
    
    async def update_profile(self, command: UpdateProfileCommand) -> UserDTO:
        """Update a user's profile.
        
        Args:
            command: The update profile command.
            
        Returns:
            DTO representing the updated user.
            
        Raises:
            ApplicationError: If profile update fails.
        """
        try:
            result = await self._update_profile_handler.handle(command)
            await self._publish_events(result.events)
            return result.user_dto
        except Exception as e:
            logger.error(f"Failed to update profile: {e}", exc_info=True)
            if isinstance(e, ApplicationError):
                raise
            raise ApplicationError(f"Profile update failed: {e}") from e
    
    async def deactivate_user(self, command: DeactivateUserCommand) -> None:
        """Deactivate a user.
        
        Args:
            command: The deactivation command.
            
        Raises:
            ApplicationError: If deactivation fails.
        """
        try:
            result = await self._deactivate_handler.handle(command)
            await self._publish_events(result.events)
        except Exception as e:
            logger.error(f"Failed to deactivate user: {e}", exc_info=True)
            if isinstance(e, ApplicationError):
                raise
            raise ApplicationError(f"User deactivation failed: {e}") from e
    
    async def _publish_events(self, events: list[DomainEvent]) -> None:
        """Publish domain events through the event bus.
        
        Args:
            events: List of domain events to publish.
        """
        for event in events:
            self._event_bus.publish(event)  # Not async