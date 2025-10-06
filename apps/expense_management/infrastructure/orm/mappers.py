"""Domain-ORM mappers for Expense Management.

This module contains mapper functions that convert between
domain entities/value objects and Django ORM models.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional

from ...domain.entities.expense import Expense
from ...domain.entities.category import Category
from ...domain.value_objects.expense_id import ExpenseId
from ...domain.value_objects.category_id import CategoryId
from ...domain.value_objects.user_id import UserId
from ...domain.value_objects.amount_tzs import AmountTZS
from ...domain.value_objects.expense_description import ExpenseDescription
from ...domain.value_objects.category_name import CategoryName
from .models import ExpenseModel, CategoryModel


def expense_model_to_entity(model: ExpenseModel) -> Expense:
    """Convert Django ExpenseModel to Expense domain entity.
    
    Args:
        model: Django ORM model instance.
        
    Returns:
        Expense domain entity with all domain value objects.
        
    Raises:
        ValueError: If model data is invalid for domain entity creation.
    """
    try:
        description = ExpenseDescription.from_string(model.description) if model.description else None
        
        return Expense(
            expense_id=ExpenseId.from_string(str(model.id)),
            user_id=UserId.from_string(str(model.user_id)),
            category_id=CategoryId.from_string(str(model.category_id)),
            amount_tzs=AmountTZS.from_decimal(model.amount_tzs),
            description=description,
            expense_date=model.expense_date,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    except Exception as e:
        raise ValueError(f"Failed to convert ExpenseModel to Expense entity: {e}") from e


def expense_entity_to_model_data(entity: Expense) -> Dict[str, Any]:
    """Convert Expense domain entity to Django model data dictionary.
    
    Args:
        entity: Expense domain entity.
        
    Returns:
        Dictionary with data suitable for Django model creation/update.
    """
    return {
        'id': entity.expense_id.value,
        'user_id': entity.user_id.value,
        'category_id': entity.category_id.value,
        'amount_tzs': entity.amount_tzs.to_decimal(),
        'description': entity.description.value if entity.description else None,
        'expense_date': entity.expense_date,
        'created_at': entity.created_at,
        'updated_at': entity.updated_at,
    }


def create_expense_model_from_entity(entity: Expense) -> ExpenseModel:
    """Create a new Django ExpenseModel from Expense domain entity.
    
    Args:
        entity: Expense domain entity.
        
    Returns:
        New ExpenseModel instance (not saved to database).
    """
    data = expense_entity_to_model_data(entity)
    return ExpenseModel(**data)


def update_expense_model_from_entity(model: ExpenseModel, entity: Expense) -> ExpenseModel:
    """Update Django ExpenseModel from Expense domain entity.
    
    Args:
        model: Existing ExpenseModel instance.
        entity: Expense domain entity with updated data.
        
    Returns:
        Updated ExpenseModel instance (not saved to database).
    """
    data = expense_entity_to_model_data(entity)
    
    for field, value in data.items():
        if hasattr(model, field):
            setattr(model, field, value)
    
    return model


def category_model_to_entity(model: CategoryModel) -> Category:
    """Convert Django CategoryModel to Category domain entity.
    
    Args:
        model: Django ORM model instance.
        
    Returns:
        Category domain entity with all domain value objects.
        
    Raises:
        ValueError: If model data is invalid for domain entity creation.
    """
    try:
        return Category(
            category_id=CategoryId.from_string(str(model.id)),
            user_id=UserId.from_string(str(model.user_id)),
            name=CategoryName.from_string(model.name),
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    except Exception as e:
        raise ValueError(f"Failed to convert CategoryModel to Category entity: {e}") from e


def category_entity_to_model_data(entity: Category) -> Dict[str, Any]:
    """Convert Category domain entity to Django model data dictionary.
    
    Args:
        entity: Category domain entity.
        
    Returns:
        Dictionary with data suitable for Django model creation/update.
    """
    return {
        'id': entity.category_id.value,
        'user_id': entity.user_id.value,
        'name': entity.name.value,
        'created_at': entity.created_at,
        'updated_at': entity.updated_at,
    }


def create_category_model_from_entity(entity: Category) -> CategoryModel:
    """Create a new Django CategoryModel from Category domain entity.
    
    Args:
        entity: Category domain entity.
        
    Returns:
        New CategoryModel instance (not saved to database).
    """
    data = category_entity_to_model_data(entity)
    return CategoryModel(**data)


def update_category_model_from_entity(model: CategoryModel, entity: Category) -> CategoryModel:
    """Update Django CategoryModel from Category domain entity.
    
    Args:
        model: Existing CategoryModel instance.
        entity: Category domain entity with updated data.
        
    Returns:
        Updated CategoryModel instance (not saved to database).
    """
    data = category_entity_to_model_data(entity)
    
    for field, value in data.items():
        if hasattr(model, field):
            setattr(model, field, value)
    
    return model


def validate_expense_model_data(data: Dict[str, Any]) -> None:
    """Validate model data for expense entity conversion.
    
    Args:
        data: Dictionary containing expense model data.
        
    Raises:
        ValueError: If data is invalid for expense entity creation.
    """
    required_fields = ['id', 'user_id', 'category_id', 'amount_tzs', 'expense_date']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if data[field] is None:
            raise ValueError(f"Field cannot be None: {field}")
    
    # Validate amount is non-negative
    if isinstance(data['amount_tzs'], (int, float, Decimal)) and data['amount_tzs'] < 0:
        raise ValueError("Amount cannot be negative")
    
    # Validate date types
    if not isinstance(data['expense_date'], (date, str)):
        raise ValueError("expense_date must be a date or string")


def validate_category_model_data(data: Dict[str, Any]) -> None:
    """Validate model data for category entity conversion.
    
    Args:
        data: Dictionary containing category model data.
        
    Raises:
        ValueError: If data is invalid for category entity creation.
    """
    required_fields = ['id', 'user_id', 'name']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if data[field] is None:
            raise ValueError(f"Field cannot be None: {field}")
    
    # Validate name is not empty
    if isinstance(data['name'], str) and not data['name'].strip():
        raise ValueError("Category name cannot be empty")


def serialize_expense_for_outbox(entity: Expense) -> Dict[str, Any]:
    """Serialize expense entity for outbox event storage.
    
    Args:
        entity: Expense domain entity.
        
    Returns:
        Serializable dictionary for JSON storage.
    """
    return {
        'id': str(entity.expense_id.value),
        'user_id': str(entity.user_id.value),
        'category_id': str(entity.category_id.value),
        'amount_tzs': float(entity.amount_tzs.value),
        'description': entity.description.value if entity.description else None,
        'expense_date': entity.expense_date.isoformat(),
        'created_at': entity.created_at.isoformat(),
        'updated_at': entity.updated_at.isoformat(),
    }


def serialize_category_for_outbox(entity: Category) -> Dict[str, Any]:
    """Serialize category entity for outbox event storage.
    
    Args:
        entity: Category domain entity.
        
    Returns:
        Serializable dictionary for JSON storage.
    """
    return {
        'id': str(entity.category_id.value),
        'user_id': str(entity.user_id.value),
        'name': entity.name.value,
        'created_at': entity.created_at.isoformat(),
        'updated_at': entity.updated_at.isoformat(),
    }