"""Dependency injection container for infrastructure services.

This module provides a simple dependency injection container
for managing infrastructure service instances and their dependencies.
"""

from typing import Optional, Protocol, TypeVar, cast

from ..domain.repositories.expense_repository import ExpenseRepository
from ..domain.repositories.category_repository import CategoryRepository
from .config import get_config
from .database.transaction_manager import (
    DjangoTransactionManager,
    create_transaction_manager,
)
from .repositories.expense_repository_django import DjangoExpenseRepository
from .repositories.category_repository_django import DjangoCategoryRepository

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
        if service_type not in self._services:
            self._services[service_type] = self._create_service(service_type)
        return self._services[service_type]  # type: ignore
    
    def _create_service(self, service_type: type[T]) -> T:
        """Create new service instance.
        
        Args:
            service_type: Type of service to create.
            
        Returns:
            New service instance.
            
        Raises:
            ValueError: If service type is not supported.
        """
        if issubclass(service_type, ExpenseRepository):
            return cast(T, DjangoExpenseRepository(
                transaction_manager=self.get(DjangoTransactionManager)
            ))
        elif issubclass(service_type, CategoryRepository):
            return cast(T, DjangoCategoryRepository(
                transaction_manager=self.get(DjangoTransactionManager)
            ))
        elif service_type == DjangoTransactionManager:
            return cast(T, create_transaction_manager())
        
        raise ValueError(f"Unknown service type: {service_type}")
    

_container: Optional[InfrastructureContainer] = None


def get_container() -> InfrastructureContainer:
    """Get global container instance.
    
    Returns:
        Current container instance.
    """
    global _container
    if _container is None:
        _container = InfrastructureContainer()
    return _container


def set_container(container: InfrastructureContainer) -> None:
    """Set global container instance.
    
    Args:
        container: New container instance.
    """
    global _container
    _container = container