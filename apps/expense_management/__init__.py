"""Expense Management Django App Configuration.

This module configures the expense management bounded context
as a Django application with proper app configuration.
"""

# Import app configuration to ensure proper Django registration
from .apps import ExpenseManagementConfig

# Set default app config for Django
default_app_config = 'expense_management.apps.ExpenseManagementConfig'
