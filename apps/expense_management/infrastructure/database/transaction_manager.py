"""Transaction management for Expense Management infrastructure.

This module provides Django-based transaction management operations
for coordinating database operations and event publishing.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

from django.db import transaction

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class DjangoTransactionManager:
    """Django-based transaction manager for expense management operations.
    
    Provides atomic transaction operations using Django's database
    transaction management capabilities.
    """
    
    def begin_transaction(self) -> None:
        """Begin a new transaction.
        
        Note: Django manages transactions automatically. This method
        is provided for protocol compliance but Django handles
        transaction lifecycle through decorators and context managers.
        """
        # Django uses context managers and decorators for transaction management
        # This is primarily for protocol compliance
        pass
    
    def commit_transaction(self) -> None:
        """Commit the current transaction.
        
        Note: Django automatically commits transactions when context
        managers or decorators complete successfully.
        """
        # Django handles commits automatically
        pass
    
    def rollback_transaction(self) -> None:
        """Rollback the current transaction.
        
        Note: Django automatically rolls back transactions on exceptions
        within transaction contexts.
        """
        transaction.rollback()
    
    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction.
        
        Returns:
            True if in a transaction, False otherwise.
        """
        return transaction.get_connection().in_atomic_block


def create_transaction_manager() -> DjangoTransactionManager:
    """Create a Django transaction manager instance.
    
    Returns:
        Configured Django transaction manager.
    """
    return DjangoTransactionManager()


@contextmanager
def django_transaction() -> Generator[None, None, None]:
    """Context manager for Django database transactions.
    
    Provides atomic transaction execution with automatic rollback
    on exceptions.
    
    Example:
        with django_transaction():
            repository.save(expense)
            outbox_writer.write_event(event)
    """
    try:
        with transaction.atomic():
            logger.debug("Starting database transaction")
            yield
            logger.debug("Transaction committed successfully")
    except Exception as e:
        logger.error(f"Transaction rolled back due to error: {e}")
        raise


def transactional(func: F) -> F:
    """Decorator for wrapping functions in database transactions.
    
    Ensures all database operations within the decorated function
    are executed atomically.
    
    Args:
        func: Function to wrap in transaction.
        
    Returns:
        Wrapped function with transaction management.
        
    Example:
        @transactional
        def create_expense_with_event(expense: Expense) -> None:
            repository.save(expense)
            outbox_writer.write_event(expense_created_event)
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with django_transaction():
            return func(*args, **kwargs)
    
    return wrapper  # type: ignore


def atomic_operation(func: F) -> F:
    """Decorator for atomic database operations.
    
    Alias for transactional decorator for backward compatibility
    and clearer semantic meaning.
    
    Args:
        func: Function to wrap in atomic operation.
        
    Returns:
        Wrapped function with atomic execution.
    """
    return transactional(func)


# Export transaction utilities
__all__ = [
    'DjangoTransactionManager',
    'create_transaction_manager',
    'django_transaction',
    'transactional',
    'atomic_operation',
]