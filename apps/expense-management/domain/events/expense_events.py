"""Domain events for expense management context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects.user.user_id import UserId
from ..value_objects.expense.expense_id import ExpenseId
from ..value_objects.category.category_id import CategoryId


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    occurred_on: datetime


@dataclass(frozen=True)
class ExpenseCreated(DomainEvent):
    """Event raised when a new expense is created."""

    expense_id: ExpenseId
    user_id: UserId
    amount_tzs: float
    description: str
    date: str
    category_id: Optional[CategoryId]


@dataclass(frozen=True)
class ExpenseUpdated(DomainEvent):
    """Event raised when an expense is updated."""

    expense_id: ExpenseId
    user_id: UserId
    amount_tzs: Optional[float] = None
    description: Optional[str] = None
    date: Optional[str] = None
    category_id: Optional[CategoryId] = None


@dataclass(frozen=True)
class ExpenseDeleted(DomainEvent):
    """Event raised when an expense is deleted."""

    expense_id: ExpenseId
    user_id: UserId


@dataclass(frozen=True)
class CategoryCreated(DomainEvent):
    """Event raised when a new category is created."""

    category_id: CategoryId
    user_id: UserId
    name: str


@dataclass(frozen=True)
class CategoryUpdated(DomainEvent):
    """Event raised when a category is updated."""

    category_id: CategoryId
    user_id: UserId
    name: str


@dataclass(frozen=True)
class CategoryDeleted(DomainEvent):
    """Event raised when a category is deleted."""

    category_id: CategoryId
    user_id: UserId