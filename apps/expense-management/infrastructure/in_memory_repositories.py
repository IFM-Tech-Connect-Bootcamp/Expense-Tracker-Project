from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime

from ..domain.repositories.expense_repository import ExpenseRepository
from ..domain.repositories.category_repository import  CategoryRepository
from ..domain.entities.expense import Expense
from ..domain.entities.category import Category


class InMemoryExpenseRepository(ExpenseRepository):
    def __init__(self):
        self.store: Dict[str, Expense] = {}

    async def add(self, expense: Expense) -> Expense:
        self.store[expense.expense_id] = expense
        return expense

    def get_by_id(self, expense_id: str) -> Optional[Expense]:
        return self.store.get(expense_id)

    def list_by_user(self, user_id: str) -> List[Expense]:
        return [e for e in self.store.values() if str(e.user_id) == user_id]

    async def update(self, expense: Expense) -> Expense:
        if expense.expense_id not in self.store:
            raise KeyError("Expense not found")
        self.store[expense.expense_id] = expense
        return expense

    def delete(self, expense_id: str) -> None:
        self.store.pop(expense_id, None)


class InMemoryCategoryRepository(CategoryRepository):
    def __init__(self):
        self.store: Dict[str, Category] = {}

    def add(self, category: Category) -> Category:
        self.store[str(category.category_id)] = category
        return category

    def exists_for_user(self, category_id: str, user_id: str) -> bool:
        cat = self.store.get(category_id)
        return bool(cat and str(cat.user_id) == user_id)
