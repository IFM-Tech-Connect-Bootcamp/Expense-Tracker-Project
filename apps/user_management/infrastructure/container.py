"""Dependency injection container for infrastructure services.

This module provides a simple dependency injection container
for managing infrastructure service instances and their dependencies.
"""

from typing import Optional, Protocol, TypeVar

from ..domain.repositories.user_repository import UserRepository
from ..domain.services.password_policy import PasswordHasher, PasswordPolicy, TokenProvider
from .adapters import InfrastructureTokenService
from .auth.bcrypt_hasher import BcryptPasswordHasher
from .auth.jwt_provider import JWTTokenProvider
from .auth.password_policy import DefaultPasswordPolicy, LenientPasswordPolicy, StrictPasswordPolicy
from .config import get_config
from .database.transaction_manager import (
    DjangoTransactionManager,
    create_transaction_manager,
)
from .repositories.user_repository_django import DjangoUserRepository

T = TypeVar('T')


class ServiceProvider(Protocol):
    """Protocol for service provider interface."""
    
    def get(self, service_type: type[T]) -> T:
        """Get service instance by type."""
        ...


class InfrastructureContainer:
    """Simple dependency injection container for infrastructure services."""
    
    def __init__(self) -> None:
        """Initialize container with lazy service creation."""
        self._services: dict[type, object] = {}
        self._config = get_config()
    
    def get(self, service_type: type[T]) -> T:
        """Get service instance by type.
        
        Args:
            service_type: Type of service to retrieve.
            
        Returns:
            Service instance.
            
        Raises:
            ValueError: If service type is not registered.
        """
        if service_type in self._services:
            return self._services[service_type]  # type: ignore
        
        # Create service instance based on type
        service = self._create_service(service_type)
        self._services[service_type] = service
        return service  # type: ignore
    
    def register(self, service_type: type[T], instance: T) -> None:
        """Register a service instance.
        
        Args:
            service_type: Type to register service under.
            instance: Service instance.
        """
        self._services[service_type] = instance
    
    def _create_service(self, service_type: type) -> object:
        """Create service instance based on type.
        
        Args:
            service_type: Type of service to create.
            
        Returns:
            Service instance.
            
        Raises:
            ValueError: If service type is not supported.
        """
        # Repository services
        if service_type == UserRepository:
            return DjangoUserRepository()
        
        # Auth services
        elif service_type == PasswordHasher:
            return BcryptPasswordHasher(
                rounds=self._config.auth.bcrypt_rounds
            )
        
        elif service_type == TokenProvider:
            return JWTTokenProvider(
                secret_key=self._config.auth.jwt_secret_key,
                algorithm=self._config.auth.jwt_algorithm,
                expiry_minutes=self._config.auth.jwt_access_token_expire_minutes,
            )
        
        elif service_type == PasswordPolicy:
            policy_type = getattr(self._config.auth, 'password_policy_type', 'default')
            if policy_type == 'lenient':
                return LenientPasswordPolicy(min_length=self._config.auth.password_min_length)
            elif policy_type == 'strict':
                return StrictPasswordPolicy()
            else:
                return DefaultPasswordPolicy(min_length=self._config.auth.password_min_length)
        
        # Concrete implementation types
        elif service_type == DjangoUserRepository:
            return DjangoUserRepository()
        
        elif service_type == InfrastructureTokenService:
            provider = JWTTokenProvider(
                secret_key=self._config.auth.jwt_secret_key,
                algorithm=self._config.auth.jwt_algorithm,
                expiry_minutes=self._config.auth.jwt_access_token_expire_minutes,
            )
            return InfrastructureTokenService(provider)
        
        elif service_type == BcryptPasswordHasher:
            return BcryptPasswordHasher(
                rounds=self._config.auth.bcrypt_rounds
            )
        
        elif service_type == JWTTokenProvider:
            return JWTTokenProvider(
                secret_key=self._config.auth.jwt_secret_key,
                algorithm=self._config.auth.jwt_algorithm,
                expiry_minutes=self._config.auth.jwt_access_token_expire_minutes,
            )
        
        elif service_type == DefaultPasswordPolicy:
            return DefaultPasswordPolicy(min_length=self._config.auth.password_min_length)
        
        elif service_type == LenientPasswordPolicy:
            return LenientPasswordPolicy(min_length=self._config.auth.password_min_length)
        
        elif service_type == StrictPasswordPolicy:
            return StrictPasswordPolicy()
        
        # Transaction manager
        elif service_type == DjangoTransactionManager:
            return create_transaction_manager()
        
        else:
            raise ValueError(f"Unknown service type: {service_type}")


# Global container instance
_container: Optional[InfrastructureContainer] = None


def get_container() -> InfrastructureContainer:
    """Get the global infrastructure container.
    
    Returns:
        InfrastructureContainer instance.
    """
    global _container
    if _container is None:
        _container = InfrastructureContainer()
    return _container


def set_container(container: InfrastructureContainer) -> None:
    """Set the global infrastructure container.
    
    Args:
        container: InfrastructureContainer instance.
    """
    global _container
    _container = container