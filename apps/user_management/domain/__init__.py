"""User Management Domain Layer

This package contains the core domain logic for user management,
including entities, value objects, services, and repository interfaces.
All code in this package is framework-agnostic and contains no Django imports.
"""

# Value Objects
from .value_objects.user_id import UserId
from .value_objects.email import Email
from .value_objects.password_hash import PasswordHash
from .value_objects.first_name import FirstName
from .value_objects.last_name import LastName

# Entities
from .entities.user import User

# Enums
from .enums.user_status import UserStatus

# Events
from .events.user_events import (
    DomainEvent,
    UserRegistered,
    UserPasswordChanged,
    UserDeactivated,
    UserProfileUpdated
)

# Services
from .services.password_policy import (
    PasswordHasher,
    TokenProvider,
    PasswordPolicy,
    UserDomainService
)

# Repositories
from .repositories.user_repository import (
    UserRepository,
    RepositoryError,
    TransactionManager
)

# Errors
from .errors import (
    UserManagementDomainError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    InvalidOperationError,
    InvalidEmailError,
    PasswordPolicyError,
    UserDeactivatedError,
    DomainValidationError
)

__all__ = [
    # Value Objects
    "UserId",
    "Email", 
    "PasswordHash",
    "FirstName",
    "LastName",
    # Entities
    "User",
    # Enums
    "UserStatus",
    # Events
    "DomainEvent",
    "UserRegistered",
    "UserPasswordChanged", 
    "UserDeactivated",
    "UserProfileUpdated",
    # Services
    "PasswordHasher",
    "TokenProvider",
    "PasswordPolicy",
    "UserDomainService",
    # Repositories
    "UserRepository",
    "RepositoryError",
    "TransactionManager",
    # Errors
    "UserManagementDomainError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "InvalidOperationError",
    "InvalidEmailError",
    "PasswordPolicyError",
    "UserDeactivatedError",
    "DomainValidationError",
]