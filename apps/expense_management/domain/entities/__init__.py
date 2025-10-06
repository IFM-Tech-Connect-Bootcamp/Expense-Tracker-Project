"""
Expense Management Domain - Entities Package

This package contains all entities for the expense management bounded context.
Entities are objects with identity that encapsulate business logic and behavior.
"""

from .expense import Expense
from .category import Category

__all__ = [
    'Expense',
    'Category'
]