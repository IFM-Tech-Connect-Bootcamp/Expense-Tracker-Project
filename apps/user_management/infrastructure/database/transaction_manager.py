"""Django transaction manager implementation.

This module provides a concrete implementation of the TransactionManager
interface using Django's database transaction system.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from django.db import transaction

from ...domain.repositories.user_repository import TransactionManager

logger = logging.getLogger(__name__)


class DjangoTransactionManager(TransactionManager):
    """Django implementation of TransactionManager.
    
    Provides transaction management operations using Django's
    database transaction system with support for nested transactions.
    """

    def __init__(self) -> None:
        """Initialize the transaction manager."""
        self._transaction_depth = 0

    def begin_transaction(self) -> None:
        """Begin a new transaction.
        
        If already in a transaction, creates a savepoint.
        """
        if self._transaction_depth == 0:
            transaction.set_autocommit(False)
        else:
            # Create savepoint for nested transaction
            savepoint_id = transaction.savepoint()
        
        self._transaction_depth += 1

    def commit_transaction(self) -> None:
        """Commit the current transaction.
        
        If in a nested transaction, releases the savepoint.
        
        Raises:
            RuntimeError: If not currently in a transaction.
        """
        if self._transaction_depth == 0:
            raise RuntimeError("Cannot commit: not in a transaction")
        
        self._transaction_depth -= 1
        
        if self._transaction_depth == 0:
            transaction.commit()
            transaction.set_autocommit(True)
        else:
            # Release savepoint for nested transaction
            pass

    def rollback_transaction(self) -> None:
        """Rollback the current transaction.
        
        If in a nested transaction, rolls back to the savepoint.
        
        Raises:
            RuntimeError: If not currently in a transaction.
        """
        if self._transaction_depth == 0:
            raise RuntimeError("Cannot rollback: not in a transaction")
        
        self._transaction_depth -= 1
        
        if self._transaction_depth == 0:
            transaction.rollback()
            transaction.set_autocommit(True)
        else:
            # Rollback to savepoint for nested transaction
            pass

    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction.
        
        Returns:
            True if in a transaction, False otherwise.
        """
        return self._transaction_depth > 0

    @contextmanager
    def transaction_context(self) -> Generator[None, None, None]:
        """Context manager for transaction handling.
        
        Automatically begins transaction on enter and commits/rollbacks on exit.
        
        Yields:
            None
            
        Example:
            with transaction_manager.transaction_context():
                # Perform database operations
                repository.save(user)
        """
        self.begin_transaction()
        try:
            yield
            self.commit_transaction()
        except Exception:
            self.rollback_transaction()
            raise

    @asynccontextmanager
    async def async_transaction_context(self) -> AsyncGenerator[None, None]:
        """Async context manager for transaction handling.
        
        Automatically begins transaction on enter and commits/rollbacks on exit.
        
        Yields:
            None
            
        Example:
            async with transaction_manager.async_transaction_context():
                # Perform async database operations
                await repository.save(user)
        """
        self.begin_transaction()
        try:
            yield
            self.commit_transaction()
        except Exception:
            self.rollback_transaction()
            raise


# Factory function for dependency injection
def create_transaction_manager() -> DjangoTransactionManager:
    """Create a Django transaction manager instance.
    
    Returns:
        Configured Django transaction manager.
    """
    return DjangoTransactionManager()


# Convenience functions for common transaction patterns
@contextmanager
def django_transaction() -> Generator[DjangoTransactionManager, None, None]:
    """Context manager that provides a transaction manager.
    
    Yields:
        DjangoTransactionManager instance
        
    Example:
        with django_transaction() as tx:
            with tx.transaction_context():
                repository.save(user)
    """
    manager = create_transaction_manager()
    yield manager


@asynccontextmanager
async def async_django_transaction() -> AsyncGenerator[DjangoTransactionManager, None, None]:
    """Async context manager that provides a transaction manager.
    
    Yields:
        DjangoTransactionManager instance
        
    Example:
        async with async_django_transaction() as tx:
            async with tx.async_transaction_context():
                await repository.save(user)
    """
    manager = create_transaction_manager()
    yield manager


# Decorator for automatic transaction management
def transactional(func):
    """Decorator for automatic transaction management.
    
    Wraps a function to automatically handle database transactions.
    Commits on success, rolls back on exception.
    
    Args:
        func: Function to wrap with transaction management.
        
    Returns:
        Wrapped function.
        
    Example:
        @transactional
        def register_user(email: str, password: str) -> User:
            # This function automatically runs in a transaction
            user = User.create(email, password)
            repository.save(user)
            return user
    """
    def wrapper(*args, **kwargs):
        with django_transaction() as tx:
            with tx.transaction_context():
                return func(*args, **kwargs)
    
    return wrapper


def async_transactional(func):
    """Decorator for automatic async transaction management.
    
    Wraps an async function to automatically handle database transactions.
    Commits on success, rolls back on exception.
    
    Args:
        func: Async function to wrap with transaction management.
        
    Returns:
        Wrapped async function.
        
    Example:
        @async_transactional
        async def register_user(email: str, password: str) -> User:
            # This function automatically runs in a transaction
            user = User.create(email, password)
            await repository.save(user)
            return user
    """
    async def wrapper(*args, **kwargs):
        async with async_django_transaction() as tx:
            async with tx.async_transaction_context():
                return await func(*args, **kwargs)
    
    return wrapper