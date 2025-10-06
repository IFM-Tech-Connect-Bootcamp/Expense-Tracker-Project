"""Category repository interface.

This module defines the repository interface for Category entity persistence.
The interface is implemented in the infrastructure layer and used by
domain services and application handlers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol

from ..entities import Category
from ..value_objects import CategoryId, UserId


class CategoryRepository(Protocol):
    """Repository interface for Category entity persistence.
    
    This protocol defines the contract for category data access operations.
    Implementations should handle the mapping between domain entities
    and the underlying storage mechanism.
    """

    def save(self, category: Category) -> Category:
        """Save a new category to the repository.
        
        Args:
            category: The category entity to save.
            
        Returns:
            The saved category entity (may include generated fields).
            
        Raises:
            DuplicateCategoryNameError: If a category with the same name exists for the user.
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def update(self, category: Category) -> Category:
        """Update an existing category in the repository.
        
        Args:
            category: The category entity with updated information.
            
        Returns:
            The updated category entity.
            
        Raises:
            CategoryNotFoundError: If the category doesn't exist.
            DuplicateCategoryNameError: If name update conflicts with existing category.
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """Find a category by its ID.
        
        Args:
            category_id: The unique identifier of the category.
            
        Returns:
            The category entity if found, None otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_user(self, user_id: UserId) -> List[Category]:
        """Find all categories for a specific user.
        
        Args:
            user_id: The user identifier.
            
        Returns:
            List of categories for the user (may be empty).
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def find_by_user_and_name(
        self, 
        user_id: UserId, 
        name: str
    ) -> Optional[Category]:
        """Find a category by user and name (for uniqueness check).
        
        Args:
            user_id: The user identifier.
            name: The category name to search for.
            
        Returns:
            The category entity if found, None otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def delete(self, category: Category) -> None:
        """Delete a category from the repository.
        
        Args:
            category: The category entity to delete.
            
        Raises:
            CategoryNotFoundError: If the category doesn't exist.
            CategoryInUseError: If the category has associated expenses.
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def delete_by_id(self, category_id: CategoryId) -> bool:
        """Delete a category by its ID.
        
        Args:
            category_id: The ID of the category to delete.
            
        Returns:
            True if deleted, False if not found.
            
        Raises:
            CategoryInUseError: If the category has associated expenses.
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def exists_by_id(self, category_id: CategoryId) -> bool:
        """Check if a category exists by its ID.
        
        Args:
            category_id: The category identifier to check.
            
        Returns:
            True if the category exists, False otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def exists_by_user_and_name(self, user_id: UserId, name: str) -> bool:
        """Check if a category with the given name exists for a user.
        
        Args:
            user_id: The user identifier.
            name: The category name to check.
            
        Returns:
            True if a category with the name exists for the user, False otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def count_by_user(self, user_id: UserId) -> int:
        """Count the number of categories for a user.
        
        Args:
            user_id: The user identifier.
            
        Returns:
            The number of categories for the user.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...

    def is_category_in_use(self, category_id: CategoryId) -> bool:
        """Check if a category is being used by any expenses.
        
        Args:
            category_id: The category identifier to check.
            
        Returns:
            True if the category is used by expenses, False otherwise.
            
        Raises:
            RepositoryError: If there's an error accessing the storage.
        """
        ...