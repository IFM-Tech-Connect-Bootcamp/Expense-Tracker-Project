"""Django ORM implementation of expense repository."""

from typing import List, Optional

from django.db import transaction
from django.db.models import Q

from ...domain.entities.expense import Expense
from ...domain.repositories.expense_repository import ExpenseRepository
from ..database.transaction_manager import TransactionManager
from ..orm.models import ExpenseModel
from ..orm.mappers import expense_from_orm, expense_to_orm


class DjangoExpenseRepository(ExpenseRepository):
    """Django ORM-based implementation of ExpenseRepository."""
    
    def __init__(self, transaction_manager: TransactionManager) -> None:
        """Initialize repository with transaction manager.
        
        Args:
            transaction_manager: Handles database transactions.
        """
        self._transaction_manager = transaction_manager

    async def add(self, expense: Expense) -> Expense:
        """Add a new expense.
        
        Args:
            expense: Expense entity to add.
            
        Returns:
            Added expense entity.
        """
        with self._transaction_manager.atomic():
            model = ExpenseModel.objects.create(**expense_to_orm(expense))
            return expense_from_orm(model)

    def get_by_id(self, expense_id: str) -> Optional[Expense]:
        """Get expense by ID.
        
        Args:
            expense_id: ID of expense to retrieve.
            
        Returns:
            Expense entity if found, None otherwise.
        """
        try:
            model = ExpenseModel.objects.get(id=expense_id)
            return expense_from_orm(model)
        except ExpenseModel.DoesNotExist:
            return None

    def list_by_user(self, user_id: str) -> List[Expense]:
        """List all expenses for a user.
        
        Args:
            user_id: ID of user to list expenses for.
            
        Returns:
            List of expense entities.
        """
        models = ExpenseModel.objects.filter(user_id=user_id)
        return [expense_from_orm(m) for m in models]

    async def update(self, expense: Expense) -> Expense:
        """Update an existing expense.
        
        Args:
            expense: Updated expense entity.
            
        Returns:
            Updated expense entity.
            
        Raises:
            KeyError: If expense does not exist.
        """
        with self._transaction_manager.atomic():
            try:
                model = ExpenseModel.objects.get(id=expense.expense_id)
                for field, value in expense_to_orm(expense).items():
                    setattr(model, field, value)
                model.save()
                return expense_from_orm(model)
            except ExpenseModel.DoesNotExist:
                raise KeyError("Expense not found")

    def delete(self, expense_id: str) -> None:
        """Delete an expense.
        
        Args:
            expense_id: ID of expense to delete.
        """
        ExpenseModel.objects.filter(id=expense_id).delete()