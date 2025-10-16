"""Service adapters for bridging infrastructure and application layers.

This module provides adapter classes that adapt infrastructure services
to match the interfaces expected by the application layer.
"""

from __future__ import annotations

from typing import Protocol

from ..domain.repositories.expense_repository import ExpenseRepository
from ..domain.repositories.category_repository import CategoryRepository


class ExpenseService(Protocol):
    """Protocol for application layer expense service."""
    
    def get_expense_repository(self) -> ExpenseRepository:
        """Get expense repository implementation."""
        ...
    
    def get_category_repository(self) -> CategoryRepository:
        """Get category repository implementation."""
        ...


class InfrastructureExpenseService:
    """Adapter for infrastructure expense services to application layer interface."""
    
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize the expense service adapter.
        
        Args:
            expense_repository: Expense repository implementation.
            category_repository: Category repository implementation.
        """
        self._expense_repository = expense_repository
        self._category_repository = category_repository

    def get_expense_repository(self) -> ExpenseRepository:
        """Get expense repository implementation."""
        return self._expense_repository
    
    def get_category_repository(self) -> CategoryRepository:
        """Get category repository implementation."""
        return self._category_repository