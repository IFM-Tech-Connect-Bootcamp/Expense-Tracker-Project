"""
Expense Management Domain - Events Package

This package contains all domain events for the expense management bounded context.
Domain events represent significant business occurrences that other parts of the system may need to react to.
"""

from .expense_events import DomainEvent, ExpenseCreated, ExpenseUpdated, ExpenseDeleted
from .category_events import CategoryCreated, CategoryUpdated, CategoryDeleted

__all__ = [
    'DomainEvent',
    'ExpenseCreated',
    'ExpenseUpdated', 
    'ExpenseDeleted',
    'CategoryCreated',
    'CategoryUpdated',
    'CategoryDeleted'
]