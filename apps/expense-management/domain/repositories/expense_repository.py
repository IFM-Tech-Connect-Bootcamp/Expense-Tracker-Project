from __future__ import annotations

from typing import Protocol, Optional, List, runtime_checkable

from entities.expense import Expense

@runtime_checkable
class ExpenseRepository(Protocol):
    """Repository interface for expenses. Infrastructure should implement this."""

    async def add(self, expense: Expense) -> Expense:
        ...

    def get_by_id(self, expense_id: str) -> Optional[Expense]:
        ...

    def list_by_user(self, user_id: str) -> List[Expense]:
        ...

    async  def update(self, expense: Expense) -> Expense:
        ...

    def delete(self, expense_id: str) -> None:
        ...


class CategoryRepository(Protocol):
    def exists_for_user(self, category_id: str, user_id: str) -> bool:
        ...
