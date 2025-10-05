"""User repository interface.

This module defines the repository interface for user persistence operations.
The interface is implemented in the infrastructure layer and used by
domain services and application handlers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Protocol

from ..entities.user import User
from ..value_objects.email import Email
from ..value_objects.user_id import UserId


class UserRepository(Protocol):
    """Repository interface for user persistence operations.
    
    This protocol defines the contract for user data access operations.
    Implementations should handle the mapping between domain entities
    and the underlying storage mechanism.
    
    All methods are async to support modern async/await patterns.
    """
    
    
    
    
    
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find a user by their unique identifier.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            The user entity if found, None otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...
    
    
    
    
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find a user by their email address.
        
        Args:
            email: The email address to search for.
            
        Returns:
            The user entity if found, None otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...
    
    
    
    
    
    async def find_active_by_email(self, email: Email) -> Optional[User]:
        """Find an active user by their email address.
        
        Args:
            email: The email address to search for.
            
        Returns:
            The active user entity if found, None otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...
    
    
    
    
    
    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user exists with the given email address.
        
        Args:
            email: The email address to check.
            
        Returns:
            True if a user exists with the email, False otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...
    
    
    
    
    
    async def save(self, user: User) -> User:
        """Save a new user to the repository.
        
        Args:
            user: The user entity to save.
            
        Returns:
            The saved user entity (may include generated fields).
            
        Raises:
            UserAlreadyExistsError: If a user with the same email already exists.
            RepositoryError: If there's an error accessing the storage.
        """
        ...
    
    
    
    
    
    async def update(self, user: User) -> User:
        """Update an existing user in the repository.
        
        Args:
            user: The user entity with updated information.
            
        Returns:
            The updated user entity.
            
        Raises:
            UserNotFoundError: If the user doesn't exist.
            UserAlreadyExistsError: If email update conflicts with existing user.
            RepositoryError: If there's an error accessing the storage.
        """
        ...
    
    
    
    
    
    async def delete(self, user_id: UserId) -> None:
        """Hard delete a user from the repository.
        
        Note: This is a hard delete operation. Consider using
        user deactivation instead for audit purposes.
        
        Args:
            user_id: The ID of the user to delete.
            
        Raises:
            UserNotFoundError: If the user doesn't exist.
            RepositoryError: If there's an error accessing the storage.
        """
        ...
    
    
    
    
    
    async def count_active_users(self) -> int:
        """Count the number of active users in the system.
        
        Returns:
            The number of active users.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...






class RepositoryError(Exception):
    """Base exception for repository-level errors.
    
    This exception is raised when there are issues with the underlying
    storage mechanism that are not related to domain business rules.
    """
    
    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        """Initialize the repository error.
        
        Args:
            message: Human-readable error message.
            cause: Optional underlying exception that caused this error.
        """
        super().__init__(message)
        self.message = message
        self.cause = cause






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