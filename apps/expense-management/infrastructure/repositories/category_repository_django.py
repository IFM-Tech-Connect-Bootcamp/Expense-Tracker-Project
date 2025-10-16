"""Django ORM implementation of category repository."""

from typing import List, Union
from ...domain.entities.category import Category
from ...domain.repositories.category_repository import CategoryRepository
from ..database.transaction_manager import TransactionManager
from ..orm.models import CategoryModel
from ..orm.mappers import category_from_orm, category_to_orm


class DjangoCategoryRepository(CategoryRepository):
    """Django ORM-based implementation of CategoryRepository."""
    
    def __init__(self, transaction_manager: TransactionManager) -> None:
        """Initialize repository with transaction manager.
        
        Args:
            transaction_manager: Handles database transactions.
        """
        self._transaction_manager = transaction_manager

    def add(self, category: Category) -> Category:
        """Add a new category.
        
        Args:
            category: Category entity to add.
            
        Returns:
            Added category entity.
            
        Raises:
            ValueError: If category with same name exists for user.
        """
        with self._transaction_manager.atomic():
            if CategoryModel.objects.filter(
                user_id=str(category.user_id),
                name=str(category.name.value)
            ).exists():
                raise ValueError("Category with this name already exists for user")
                
            model = CategoryModel.objects.create(**category_to_orm(category))
            return category_from_orm(model)

    def exists_for_user(self, category_id: str, user_id: str) -> bool:
        """Check if category exists for user.
        
        Args:
            category_id: ID of category to check.
            user_id: ID of user to check for.
            
        Returns:
            True if category exists for user, False otherwise.
        """
        return CategoryModel.objects.filter(
            id=category_id,
            user_id=user_id
        ).exists()

    def get_by_id(self, category_id: str) -> Union[Category, None]:
        raise NotImplementedError

    def list_by_user(self, user_id: str) -> List[Category]:
        raise NotImplementedError

    def update(self, category: Category) -> Category:
        raise NotImplementedError

    def delete(self, category_id: str) -> None:
        raise NotImplementedError
