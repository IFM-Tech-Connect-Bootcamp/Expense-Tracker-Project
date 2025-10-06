"""
Expense Management Domain - Category Validation Service

This module contains the CategoryValidationService for category validation and business rules.
Domain services contain pure business logic without infrastructure dependencies.
"""

from typing import Optional, List

from ..entities import Category
from ..value_objects import UserId, CategoryId, CategoryName
from ..errors import (
    DuplicateCategoryNameError, BusinessRuleViolationError
)


class CategoryValidationService:
    """
    Domain service for category validation and business rules.
    
    Ensures category operations follow business rules and constraints.
    This service operates on data passed to it, following Clean Architecture principles.
    """

    @staticmethod
    def validate_category_name_unique_for_user(
        existing_categories: List[Category],
        user_id: UserId, 
        name: str,
        exclude_category_id: Optional[CategoryId] = None
    ) -> None:
        """Validate that a category name is unique for a user."""
        normalized_name = name.strip().lower()
        
        for category in existing_categories:
            if category.user_id == user_id:
                existing_name = category.name.value.strip().lower()
                if existing_name == normalized_name:
                    # If we're updating a category, exclude the current category from uniqueness check
                    if exclude_category_id is None or category.category_id != exclude_category_id:
                        raise DuplicateCategoryNameError(name, str(user_id))

    @staticmethod
    def validate_category_ownership(
        category: Category, 
        user_id: UserId
    ) -> None:
        """Validate that a category belongs to the specified user."""
        if not category.belongs_to(user_id):
            raise BusinessRuleViolationError(
                "category_ownership",
                f"Category {category.category_id} does not belong to user {user_id}"
            )

    @staticmethod
    def validate_category_name_format(name: str) -> CategoryName:
        """Validate and create a CategoryName from string input."""
        # This will raise ValueError if invalid, which is appropriate for domain validation
        return CategoryName.from_string(name)

    @staticmethod
    def validate_default_category_rules(
        category: Category,
        total_categories_for_user: int
    ) -> None:
        """Validate business rules specific to default categories."""
        # Business rule: User must have at least one category
        if total_categories_for_user <= 1:
            raise BusinessRuleViolationError(
                "minimum_categories",
                "User must have at least one category"
            )
        
        # Add other default category business rules here as needed