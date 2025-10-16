from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List
from typing_extensions import runtime_checkable

from ..entities.category import Category

@runtime_checkable
class CategoryRepository(ABC):
    """Repository interface for categories."""

    @abstractmethod
    def add(self, category: Category) -> Category:
        """Add a new category."""
        ...

    @abstractmethod
    def get_by_id(self, category_id: str) -> Optional[Category]:
        """Get a category by its ID."""
        ...

    @abstractmethod
    def list_by_user(self, user_id: str) -> List[Category]:
        """List all categories for a user."""
        ...

    @abstractmethod
    def exists_for_user(self, category_id: str, user_id: str) -> bool:
        """Check if a category exists and belongs to the given user."""
        ...

    @abstractmethod
    def update(self, category: Category) -> Category:
        """Update an existing category."""
        ...

    @abstractmethod
    def delete(self, category_id: str) -> None:
        """Delete a category by its ID."""
        ...