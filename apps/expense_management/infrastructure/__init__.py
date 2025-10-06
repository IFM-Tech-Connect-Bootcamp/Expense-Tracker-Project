"""Infrastructure layer for Expense Management.

This module provides concrete implementations of domain repositories,
event handling, and infrastructure services using Django ORM and
the transactional outbox pattern.
"""

from .container import get_container, set_container, InfrastructureContainer
from .config import get_config, set_config, InfrastructureConfig
from .repositories import DjangoExpenseRepository, DjangoCategoryRepository
from .outbox import create_outbox_writer, create_outbox_dispatcher
from .database import (
    DjangoTransactionManager, 
    create_transaction_manager,
    django_transaction,
    transactional,
    atomic_operation
)
from .subscribers import (
    # Application-level logging (sync)
    log_expense_events,
    
    # Infrastructure-level outbox integration (async)
    on_expense_created,
    on_expense_updated,
    on_expense_deleted,
    on_category_created,
    on_category_updated,
    on_category_deleted,
)

__all__ = [
    # Dependency injection
    'get_container',
    'set_container', 
    'InfrastructureContainer',
    
    # Configuration
    'get_config',
    'set_config',
    'InfrastructureConfig',
    
    # Repository implementations
    'DjangoExpenseRepository',
    'DjangoCategoryRepository',
    
    # Outbox services
    'create_outbox_writer',
    'create_outbox_dispatcher',
    
    # Transaction management
    'DjangoTransactionManager',
    'create_transaction_manager',
    'django_transaction',
    'transactional',
    'atomic_operation',
    
    # Event subscribers
    'log_expense_events',          # Sync logging subscriber
    'on_expense_created',          # Async outbox subscriber  
    'on_expense_updated',          # Async outbox subscriber
    'on_expense_deleted',          # Async outbox subscriber
    'on_category_created',         # Async outbox subscriber
    'on_category_updated',         # Async outbox subscriber
    'on_category_deleted',         # Async outbox subscriber
]