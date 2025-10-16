"""Django transaction management.

This module provides transaction management abstractions
for working with Django database transactions.
"""

from typing import ContextManager, TypeVar

from django.db import transaction
from typing_extensions import Protocol

T = TypeVar('T')


class TransactionManager(Protocol):
    """Protocol for transaction management."""
    
    def atomic(self) -> ContextManager[None]:
        """Context manager for atomic transactions."""
        ...


class DjangoTransactionManager:
    """Django-based transaction manager."""
    
    def atomic(self) -> ContextManager[None]:
        """Create atomic transaction context.
        
        Returns:
            Context manager for transaction.
        """
        return transaction.atomic()


def create_transaction_manager() -> DjangoTransactionManager:
    """Create new transaction manager.
    
    Returns:
        Configured transaction manager.
    """
    return DjangoTransactionManager()