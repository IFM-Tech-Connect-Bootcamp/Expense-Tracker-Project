"""
Expense Management Domain - Repositories Package

This package contains all repository interfaces for the expense management bounded context.
Repository interfaces define contracts for data persistence without specifying implementation details.
"""

from .expense_repository import ExpenseRepository
from .category_repository import CategoryRepository


class RepositoryError(Exception):
    """Base exception for repository-level errors.
    
    This exception is raised when there are issues with the underlying
    storage mechanism that are not related to domain business rules.
    """
    
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize the repository error.
        
        Args:
            message: Human-readable error message.
            cause: Optional underlying exception that caused this error.
        """
        super().__init__(message)
        self.message = message
        self.cause = cause


from typing import Protocol


class TransactionManager(Protocol):
    """Interface for managing database transactions.
    
    This protocol defines the contract for transaction management
    operations that may be needed by application services.
    """
    
    def begin_transaction(self) -> None:
        """Begin a new transaction."""
        ...
    
    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        ...
    
    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        ...
    
    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction.
        
        Returns:
            True if in a transaction, False otherwise.
        """
        ...


__all__ = [
    'ExpenseRepository',
    'CategoryRepository',
    'RepositoryError',
    'TransactionManager'
]