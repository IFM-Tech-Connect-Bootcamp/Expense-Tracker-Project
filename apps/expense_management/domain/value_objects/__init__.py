"""
Expense Management Domain - Value Objects Package

This package contains all value objects for the expense management bounded context.
Value objects are immutable objects that represent concepts with no identity.
"""

from .expense_id import ExpenseId
from .category_id import CategoryId
from .user_id import UserId
from .amount_tzs import AmountTZS
from .expense_description import ExpenseDescription
from .category_name import CategoryName

__all__ = [
    'ExpenseId',
    'CategoryId', 
    'UserId',
    'AmountTZS',
    'ExpenseDescription',
    'CategoryName'
]