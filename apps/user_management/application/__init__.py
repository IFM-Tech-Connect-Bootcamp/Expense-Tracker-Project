"""Application layer for User Management bounded context.

This layer orchestrates business use cases by coordinating between
the domain layer and infrastructure concerns.
"""

from .commands import (
    AuthenticateUserCommand,
    ChangePasswordCommand,
    DeactivateUserCommand, 
    RegisterUserCommand,
    UpdateProfileCommand,
)
from .dto import (
    AuthResultDTO,
    UserDTO,
)
from .errors import (
    ApplicationError,
    AuthenticationFailedError,
    PasswordChangeFailedError,
    ProfileUpdateFailedError,
    RegistrationFailedError,
    UserDeactivationFailedError,
    UserNotFoundError,
    ValidationError,
)
from .event_bus import EventBus
from .handlers import (
    AuthenticateUserHandler,
    ChangePasswordHandler,
    DeactivateUserHandler,
    RegisterUserHandler,
    UpdateProfileHandler,
)
from .service import UserManagementService
from .subscribers import (
    log_user_events,
)

__all__ = [
    # Commands
    "AuthenticateUserCommand",
    "ChangePasswordCommand", 
    "DeactivateUserCommand",
    "RegisterUserCommand",
    "UpdateProfileCommand",
    # DTOs
    "AuthResultDTO",
    "UserDTO",
    # Errors
    "ApplicationError",
    "AuthenticationFailedError",
    "PasswordChangeFailedError",
    "ProfileUpdateFailedError",
    "RegistrationFailedError",
    "UserDeactivationFailedError",
    "UserNotFoundError",
    "ValidationError",
    # Event Bus
    "EventBus",
    # Handlers
    "AuthenticateUserHandler",
    "ChangePasswordHandler",
    "DeactivateUserHandler",
    "RegisterUserHandler", 
    "UpdateProfileHandler",
    # Service
    "UserManagementService",
    # Subscribers
    "log_user_events",
]