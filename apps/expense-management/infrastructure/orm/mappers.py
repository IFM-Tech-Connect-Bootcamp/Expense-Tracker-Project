"""Mapper classes for converting between ORM and domain models."""

from decimal import Decimal
from typing import Any

from domain.entities.expense import Expense
from domain.entities.category import Category
from domain.value_objects.user.user_id import UserId
from domain.value_objects.expense.amount_tzs import AmountTZS
from domain.value_objects.expense.description import Description
from domain.value_objects.expense.date import Date
from domain.value_objects.category.category_id import CategoryId
from domain.value_objects.category.name import CategoryName

from .models import ExpenseModel, CategoryModel


def expense_to_orm(expense: Expense) -> dict[str, Any]:
    """Convert expense entity to ORM model.
    
    Args:
        expense: Domain expense entity.
        
    Returns:
        Dictionary of ORM model fields.
    """
    return {
        'id': expense.expense_id,
        'user_id': str(expense.user_id),
        'amount_tzs': Decimal(str(expense.amount_tzs.value)),
        'description': str(expense.description.value),
        'date': expense.date.value,
        'category_id': str(expense.category_id) if expense.category_id else None,
    }

def expense_from_orm(model: ExpenseModel) -> Expense:
    """Convert ORM model to expense entity.
    
    Args:
        model: ORM expense model.
        
    Returns:
        Domain expense entity.
    """
    return Expense(
        expense_id=str(model.id),
        user_id=UserId.from_string(str(model.user_id)),
        amount_tzs=AmountTZS.from_string(model.amount_tzs.to_eng_string()),
        description=Description.from_string(model.description),
        date=Date.from_string(str(model.date)),
        category_id=CategoryId.from_string(str(model.category_id)) if model.category_id else None,
    )


def category_to_orm(category: Category) -> dict[str, Any]:
    """Convert category entity to ORM model.
    
    Args:
        category: Domain category entity.
        
    Returns:
        Dictionary of ORM model fields.
    """
    return {
        'id': category.category_id,
        'user_id': str(category.user_id),
        'name': str(category.name.value),
    }


def category_from_orm(model: CategoryModel) -> Category:
    """Convert ORM model to category entity.
    
    Args:
        model: ORM category model.
        
    Returns:
        Domain category entity.
    """
    return Category(
        category_id=CategoryId.from_string(str(model.id)),
        user_id=UserId.from_string(str(model.user_id)),
        name=CategoryName.from_string(model.name),
    )