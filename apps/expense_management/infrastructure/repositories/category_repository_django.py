"""Django implementation of CategoryRepository.

This module provides a concrete implementation of the CategoryRepository
interface using Django ORM for persistence.
"""

from __future__ import annotations

import logging
from typing import Optional, List

from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist

from ...domain.entities.category import Category
from ...domain.errors import CategoryNotFoundError, CategoryAlreadyExistsError
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.value_objects.category_id import CategoryId
from ...domain.value_objects.user_id import UserId
from ...domain.value_objects.category_name import CategoryName
from ..orm.mappers import (
    category_model_to_entity,
    category_entity_to_model_data,
    create_category_model_from_entity,
    update_category_model_from_entity,
    validate_category_model_data,
)
from ..orm.models import CategoryModel

logger = logging.getLogger(__name__)


class DjangoCategoryRepository(CategoryRepository):
    """Django ORM implementation of CategoryRepository.
    
    Provides persistence operations for Category entities using Django ORM.
    Handles mapping between domain entities and database models.
    Translates database errors to domain errors.
    """

    def find_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """Find category by ID.
        
        Args:
            category_id: Unique category identifier.
            
        Returns:
            Category entity if found, None otherwise.
            
        Raises:
            ValueError: If database data is invalid for domain entity.
        """
        logger.debug(f"Finding category by ID: {category_id.value}")
        
        try:
            model = CategoryModel.objects.get(id=category_id.value)
            category = category_model_to_entity(model)
            logger.debug(f"Found category: {category.category_id.value}")
            return category
        except ObjectDoesNotExist:
            logger.debug(f"Category not found: {category_id.value}")
            return None
        except Exception as e:
            logger.error(f"Error finding category by ID {category_id.value}: {e}")
            raise ValueError(f"Failed to find category: {e}") from e

    def find_by_user_id(self, user_id: UserId, limit: int = 100, offset: int = 0) -> List[Category]:
        """Find categories by user ID with pagination.
        
        Args:
            user_id: User identifier.
            limit: Maximum number of categories to return.
            offset: Number of categories to skip.
            
        Returns:
            List of category entities belonging to the user.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding categories for user: {user_id.value} (limit={limit}, offset={offset})")
        
        try:
            models = CategoryModel.objects.filter(
                user_id=user_id.value
            ).order_by('name')[offset:offset + limit]
            
            categories = []
            for model in models:
                category = category_model_to_entity(model)
                categories.append(category)
            
            logger.debug(f"Found {len(categories)} categories for user {user_id.value}")
            return categories
            
        except Exception as e:
            logger.error(f"Error finding categories for user {user_id.value}: {e}")
            raise ValueError(f"Failed to find categories: {e}") from e

    def find_by_user_and_name(self, user_id: UserId, name: CategoryName) -> Optional[Category]:
        """Find category by user and name.
        
        Args:
            user_id: User identifier.
            name: Category name to search for.
            
        Returns:
            Category entity if found, None otherwise.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding category for user {user_id.value} with name: {name.value}")
        
        try:
            model = CategoryModel.objects.filter(
                user_id=user_id.value,
                name=name.value
            ).first()
            
            if model:
                category = category_model_to_entity(model)
                logger.debug(f"Found category: {category.category_id.value}")
                return category
            
            logger.debug(f"No category found for user {user_id.value} with name {name.value}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding category by user {user_id.value} and name {name.value}: {e}")
            raise ValueError(f"Failed to find category: {e}") from e

    def exists_by_user_and_name(self, user_id: UserId, name: CategoryName) -> bool:
        """Check if category exists for user with given name.
        
        Args:
            user_id: User identifier.
            name: Category name to check.
            
        Returns:
            True if category exists, False otherwise.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Checking if category exists for user {user_id.value} with name: {name.value}")
        
        try:
            exists = CategoryModel.objects.filter(
                user_id=user_id.value,
                name=name.value
            ).exists()
            logger.debug(f"Category exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking category existence for user {user_id.value} and name {name.value}: {e}")
            raise ValueError(f"Failed to check category existence: {e}") from e

    def exists_by_id(self, category_id: CategoryId) -> bool:
        """Check if category exists by ID.
        
        Args:
            category_id: Category identifier.
            
        Returns:
            True if category exists, False otherwise.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Checking if category exists: {category_id.value}")
        
        try:
            exists = CategoryModel.objects.filter(id=category_id.value).exists()
            logger.debug(f"Category exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking category existence {category_id.value}: {e}")
            raise ValueError(f"Failed to check category existence: {e}") from e

    def count_by_user(self, user_id: UserId) -> int:
        """Count categories for a user.
        
        Args:
            user_id: User identifier.
            
        Returns:
            Number of categories for the user.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Counting categories for user: {user_id.value}")
        
        try:
            count = CategoryModel.objects.filter(user_id=user_id.value).count()
            logger.debug(f"Found {count} categories for user {user_id.value}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting categories for user {user_id.value}: {e}")
            raise ValueError(f"Failed to count categories: {e}") from e

    def save(self, category: Category) -> Category:
        """Save new category to database.
        
        Args:
            category: Category entity to save.
            
        Returns:
            Saved category entity with any generated fields.
            
        Raises:
            CategoryAlreadyExistsError: If category with same name already exists for user.
            ValueError: If category data is invalid.
        """
        logger.debug(f"Saving new category: {category.name.value} for user {category.user_id.value}")
        
        try:
            # Check if category already exists for this user
            if self.exists_by_user_and_name(category.user_id, category.name):
                raise CategoryAlreadyExistsError(
                    f"Category '{category.name.value}' already exists for user {category.user_id.value}"
                )
            
            # Create new model
            model_data = category_entity_to_model_data(category)
            validate_category_model_data(model_data)
            
            model = CategoryModel.objects.create(**model_data)
            logger.info(f"Category saved with ID: {model.id}")
            
            # Convert back to entity and return
            saved_category = category_model_to_entity(model)
            return saved_category
                
        except IntegrityError as e:
            logger.error(f"Database integrity error saving category: {e}")
            if "unique" in str(e).lower() and "name" in str(e).lower():
                raise CategoryAlreadyExistsError(
                    f"Category '{category.name.value}' already exists for user {category.user_id.value}"
                )
            raise ValueError(f"Invalid category data: {e}")
        except Exception as e:
            logger.error(f"Error saving category {category.name.value}: {e}")
            raise

    def update(self, category: Category) -> Category:
        """Update existing category entity in database.
        
        Args:
            category: Category entity to update.
            
        Returns:
            Updated category entity.
            
        Raises:
            CategoryNotFoundError: If category doesn't exist.
            CategoryAlreadyExistsError: If name change conflicts with existing category.
            ValueError: If update operation fails.
        """
        logger.debug(f"Updating category: {category.category_id.value}")
        
        try:
            # Get existing model
            try:
                existing_model = CategoryModel.objects.get(id=category.category_id.value)
            except ObjectDoesNotExist:
                logger.warning(f"Category not found for update: {category.category_id.value}")
                raise CategoryNotFoundError(str(category.category_id.value))
            
            # Check if name change conflicts with existing category
            if existing_model.name != category.name.value:
                if self.exists_by_user_and_name(category.user_id, category.name):
                    raise CategoryAlreadyExistsError(
                        f"Category '{category.name.value}' already exists for user {category.user_id.value}"
                    )
            
            # Update model with new data
            try:
                updated_model = update_category_model_from_entity(existing_model, category)
                updated_model.save()
            except IntegrityError as e:
                if 'unique' in str(e).lower() and 'name' in str(e).lower():
                    logger.warning(f"Category name already exists during update: {category.name.value}")
                    raise CategoryAlreadyExistsError(
                        f"Category '{category.name.value}' already exists for user {category.user_id.value}"
                    ) from e
                raise ValueError(f"Database integrity error: {e}") from e
            
            # Return updated entity
            updated_category = category_model_to_entity(updated_model)
                
            logger.info(f"Successfully updated category: {category.category_id.value}")
            return updated_category
            
        except (CategoryNotFoundError, CategoryAlreadyExistsError):
            raise
        except Exception as e:
            logger.error(f"Error updating category {category.category_id.value}: {e}")
            raise ValueError(f"Failed to update category: {e}") from e

    def delete(self, category_id: CategoryId) -> None:
        """Delete category from database.
        
        Args:
            category_id: ID of category to delete.
            
        Raises:
            CategoryNotFoundError: If category doesn't exist.
            ValueError: If delete operation fails.
        """
        logger.debug(f"Deleting category: {category_id.value}")
        
        try:
            try:
                model = CategoryModel.objects.get(id=category_id.value)
                model.delete()
            except ObjectDoesNotExist:
                logger.warning(f"Category not found for deletion: {category_id.value}")
                raise CategoryNotFoundError(str(category_id.value))
            
            logger.info(f"Successfully deleted category: {category_id.value}")
            
        except CategoryNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting category {category_id.value}: {e}")
            raise ValueError(f"Failed to delete category: {e}") from e

    def find_all_by_user(self, user_id: UserId) -> List[Category]:
        """Find all categories for a user (no pagination).
        
        Args:
            user_id: User identifier.
            
        Returns:
            List of all category entities for the user.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding all categories for user: {user_id.value}")
        
        try:
            models = CategoryModel.objects.filter(
                user_id=user_id.value
            ).order_by('name')
            
            categories = []
            for model in models:
                category = category_model_to_entity(model)
                categories.append(category)
            
            logger.debug(f"Found {len(categories)} categories for user {user_id.value}")
            return categories
            
        except Exception as e:
            logger.error(f"Error finding all categories for user {user_id.value}: {e}")
            raise ValueError(f"Failed to find categories: {e}") from e

    def find_categories_with_expenses(self, user_id: UserId) -> List[Category]:
        """Find categories that have associated expenses for a user.
        
        Args:
            user_id: User identifier.
            
        Returns:
            List of category entities that have expenses.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding categories with expenses for user: {user_id.value}")
        
        try:
            from ..orm.models import ExpenseModel
            
            # Get category IDs that have expenses
            category_ids = ExpenseModel.objects.filter(
                user_id=user_id.value
            ).values_list('category_id', flat=True).distinct()
            
            # Get category models
            models = CategoryModel.objects.filter(
                id__in=category_ids,
                user_id=user_id.value
            ).order_by('name')
            
            categories = []
            for model in models:
                category = category_model_to_entity(model)
                categories.append(category)
            
            logger.debug(f"Found {len(categories)} categories with expenses for user {user_id.value}")
            return categories
            
        except Exception as e:
            logger.error(f"Error finding categories with expenses for user {user_id.value}: {e}")
            raise ValueError(f"Failed to find categories with expenses: {e}") from e