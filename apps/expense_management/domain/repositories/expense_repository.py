"""Expense repository interface.

This module defines the repository interface for Expense entity persistence.
The interface is implemented in the infrastructure layer and used by
domain services and application handlers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Protocol

from ..entities import Expense
from ..value_objects import ExpenseId, CategoryId, UserId


class ExpenseRepository(Protocol):
    """Repository interface for Expense entity persistence.
    
    This protocol defines the contract for expense data access operations.
    Implementations should handle the mapping between domain entities
    and the underlying storage mechanism.
    """

    def save(self, expense: Expense) -> Expense:
        """Save a new expense to the repository.
        
        Args:
            expense: The expense entity to save.
            
        Returns:
            The saved expense entity (may include generated fields).
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def update(self, expense: Expense) -> Expense:
        """Update an existing expense in the repository.
        
        Args:
            expense: The expense entity with updated information.
            
        Returns:
            The updated expense entity.
            
        Raises:
            ExpenseNotFoundError: If the expense doesn't exist.
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_id(self, expense_id: ExpenseId) -> Optional[Expense]:
        """Find an expense by its ID.
        
        Args:
            expense_id: The unique identifier of the expense.
            
        Returns:
            The expense entity if found, None otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_user(self, user_id: UserId) -> List[Expense]:
        """Find all expenses for a specific user.
        
        Args:
            user_id: The user identifier.
            
        Returns:
            List of expenses for the user (may be empty).
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_user_and_category(
        self, 
        user_id: UserId, 
        category_id: CategoryId
    ) -> List[Expense]:
        """Find all expenses for a specific user in a specific category.
        
        Args:
            user_id: The user identifier.
            category_id: The category identifier.
            
        Returns:
            List of expenses for the user in the category (may be empty).
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_user_and_date_range(
        self, 
        user_id: UserId, 
        start_date: date, 
        end_date: date
    ) -> List[Expense]:
        """Find all expenses for a user within a date range.
        
        Args:
            user_id: The user identifier.
            start_date: Start date of the range (inclusive).
            end_date: End date of the range (inclusive).
            
        Returns:
            List of expenses within the date range (may be empty).
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_user_category_and_date_range(
        self, 
        user_id: UserId,
        category_id: CategoryId,
        start_date: date, 
        end_date: date
    ) -> List[Expense]:
        """Find expenses for a user in a category within a date range.
        
        Args:
            user_id: The user identifier.
            category_id: The category identifier.
            start_date: Start date of the range (inclusive).
            end_date: End date of the range (inclusive).
            
        Returns:
            List of expenses matching the criteria (may be empty).
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def delete(self, expense: Expense) -> None:
        """Delete an expense from the repository.
        
        Args:
            expense: The expense entity to delete.
            
        Raises:
            ExpenseNotFoundError: If the expense doesn't exist.
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def delete_by_id(self, expense_id: ExpenseId) -> bool:
        """Delete an expense by its ID.
        
        Args:
            expense_id: The ID of the expense to delete.
            
        Returns:
            True if deleted, False if not found.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def exists_by_id(self, expense_id: ExpenseId) -> bool:
        """Check if an expense exists by its ID.
        
        Args:
            expense_id: The expense identifier to check.
            
        Returns:
            True if the expense exists, False otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def count_by_user(self, user_id: UserId) -> int:
        """Count the number of expenses for a user.
        
        Args:
            user_id: The user identifier.
            
        Returns:
            The number of expenses for the user.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def count_by_category(self, category_id: CategoryId) -> int:
        """Count the number of expenses in a category.
        
        Args:
            category_id: The category identifier.
            
        Returns:
            The number of expenses in the category.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...