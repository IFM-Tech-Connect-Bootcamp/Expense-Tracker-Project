"""
Django models for expense_management app.

This module imports and exposes the Django ORM models from the infrastructure layer
to Django's migration system and admin interface.
"""

# Import infrastructure models to make them discoverable by Django
from .infrastructure.orm.models import ExpenseModel, CategoryModel, OutboxEvent

# Make models available at app level for Django
__all__ = [
    'ExpenseModel',
    'CategoryModel', 
    'OutboxEvent',
]