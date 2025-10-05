"""Infrastructure layer for user management.

This layer provides concrete implementations of domain service interfaces
using Django ORM, external libraries, and infrastructure concerns.

The infrastructure layer includes:
- ORM models and database persistence
- Authentication services (password hashing, JWT tokens)
- Repository implementations
- Event outbox for reliable message delivery
- External service integrations
- Dependency injection container
- Configuration management

All implementations follow the repository and service patterns
defined in the domain layer, ensuring clean separation of concerns
and testability.

Key Features:
- Transactional outbox pattern for reliable event delivery
- Async/await support throughout
- Type-safe Protocol-based interfaces
- Comprehensive error translation
- Configurable authentication services
- Background event processing
"""

from .adapters import (
    InfrastructurePasswordService,
    InfrastructureTokenService,
    create_password_service,
    create_token_service,
)
from .auth.bcrypt_hasher import BcryptPasswordHasher
from .auth.jwt_provider import JWTTokenProvider
from .auth.password_policy import DefaultPasswordPolicy, LenientPasswordPolicy, StrictPasswordPolicy
from .config import AuthConfig, InfrastructureConfig, OutboxConfig, get_config, set_config
from .container import InfrastructureContainer, get_container, set_container
from .database import (
    DjangoTransactionManager,
    async_django_transaction,
    async_transactional,
    create_transaction_manager,
    django_transaction,
    transactional,
)
from .orm.mappers import entity_to_model_data, model_to_entity
from .orm.models import OutboxEvent, UserModel
from .outbox.dispatcher import OutboxDispatcher
from .outbox.writer import OutboxEventWriter, write_domain_event
from .repositories.user_repository_django import DjangoUserRepository
from .subscribers import (
    on_user_deactivated,
    on_user_password_changed,
    on_user_profile_updated,
    on_user_registered,
)

# Infrastructure service implementations
__all__ = [
    # ORM
    "UserModel",
    "OutboxEvent", 
    "model_to_entity",
    "entity_to_model_data",
    
    # Repository
    "DjangoUserRepository",
    
    # Service adapters
    "InfrastructurePasswordService",
    "InfrastructureTokenService", 
    "create_password_service",
    "create_token_service",
    
    # Auth services
    "BcryptPasswordHasher",
    "JWTTokenProvider",
    "DefaultPasswordPolicy",
    "LenientPasswordPolicy",
    "StrictPasswordPolicy",
    
    # Transaction management
    "DjangoTransactionManager",
    "create_transaction_manager",
    "django_transaction",
    "async_django_transaction",
    "transactional",
    "async_transactional",
    
    # Outbox
    "OutboxEventWriter",
    "OutboxDispatcher",
    "write_domain_event",
    
    # Configuration
    "AuthConfig",
    "OutboxConfig", 
    "InfrastructureConfig",
    "get_config",
    "set_config",
    
    # Dependency injection
    "InfrastructureContainer",
    "get_container",
    "set_container",
    
    # Event subscribers
    "on_user_registered",
    "on_user_password_changed",
    "on_user_profile_updated", 
    "on_user_deactivated",
]