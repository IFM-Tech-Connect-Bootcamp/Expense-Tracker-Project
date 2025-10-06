"""Dependency injection container for infrastructure services.

This module provides a simple dependency injection container for managing
infrastructure service instances and their dependencies.
"""

from typing import Optional, TypeVar, Protocol

from ..domain.repositories.expense_repository import ExpenseRepository
from ..domain.repositories.category_repository import CategoryRepository
from ..domain.repositories import TransactionManager
from .repositories import DjangoExpenseRepository, DjangoCategoryRepository
from .outbox.writer import OutboxEventWriter, create_outbox_writer
from .outbox.dispatcher import OutboxDispatcher, create_outbox_dispatcher
from .database import DjangoTransactionManager, create_transaction_manager
from .config import get_config, InfrastructureConfig

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
        # Repository services (protocol interfaces)
        if service_type == ExpenseRepository:
            return DjangoExpenseRepository()
        
        elif service_type == CategoryRepository:
            return DjangoCategoryRepository()
        
        # Concrete repository implementations
        elif service_type == DjangoExpenseRepository:
            return DjangoExpenseRepository()
        
        elif service_type == DjangoCategoryRepository:
            return DjangoCategoryRepository()
        
        # Outbox services
        elif service_type == OutboxEventWriter:
            return create_outbox_writer(use_transaction_commit=True)
        
        elif service_type == OutboxDispatcher:
            return create_outbox_dispatcher(
                max_retries=self._config.outbox.max_retry_attempts,
                retry_delay_minutes=self._config.outbox.retry_delay_seconds // 60,
                batch_size=self._config.outbox.batch_size
            )
        
        # Transaction manager
        elif service_type == TransactionManager:
            return create_transaction_manager()
        
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