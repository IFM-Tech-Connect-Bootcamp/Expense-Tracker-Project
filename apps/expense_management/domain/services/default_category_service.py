"""
Expense Management Domain - Default Category Service

This module contains the DefaultCategoryService for managing default categories.
Domain services contain pure business logic without infrastructure dependencies.
"""

from typing import List

from ..entities import Category
from ..value_objects import UserId, CategoryName


class DefaultCategoryService:
    """
    Domain service for managing default categories.
    
    Provides business logic for creating and managing default categories for new users.
    This service provides pure domain logic without infrastructure dependencies.
    """

    DEFAULT_CATEGORIES = [
        "Food & Dining",
        "Transportation", 
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Health & Medical",
        "Travel",
        "Education",
        "Personal Care",
        "Other"
    ]

    @staticmethod
    def create_default_categories_for_user(user_id: UserId) -> List[Category]:
        """Create default category entities for a new user.
        
        Returns a list of Category entities that should be persisted.
        The application layer is responsible for checking existence and persistence.
        """
        default_categories = []
        
        for category_name in DefaultCategoryService.DEFAULT_CATEGORIES:
            category = Category.create(user_id, CategoryName.from_string(category_name))
            default_categories.append(category)
        
        return default_categories

    @staticmethod
    def get_default_category_names() -> List[str]:
        """Get the list of default category names."""
        return DefaultCategoryService.DEFAULT_CATEGORIES.copy()

    @staticmethod
    def is_default_category(category_name: str) -> bool:
        """Check if a category name is one of the default categories."""
        return category_name in DefaultCategoryService.DEFAULT_CATEGORIES

    @staticmethod
    def validate_user_has_minimum_categories(
        existing_categories: List[Category],
        minimum_required: int = 1
    ) -> bool:
        """Validate that a user has the minimum required number of categories."""
        return len(existing_categories) >= minimum_required