"""
URL configuration for Expense Management API endpoints.

This module defines the URL patterns for the expense management presentation layer,
mapping HTTP endpoints to their corresponding view functions.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    create_expense,
    update_expense,
    delete_expense,
    get_expense_summary,
    create_category,
    update_category,
    delete_category,
    expense_health_check,
)


# Define URL patterns for the expense management API
urlpatterns = [
    # Health check
    path('health/', expense_health_check, name='expense_health_check'),
    
    # Category endpoints (must come before <str:expense_id>/ patterns)
    path('categories/', create_category, name='create_category'),
    path('categories/<str:category_id>/', update_category, name='update_category'),
    path('categories/<str:category_id>/delete/', delete_category, name='delete_category'),
    
    # Summary endpoint (must come before <str:expense_id>/ patterns)
    path('summary/', get_expense_summary, name='get_expense_summary'),
    
    # Expense endpoints (generic patterns come last)
    path('', create_expense, name='create_expense'),
    path('<str:expense_id>/', update_expense, name='update_expense'),
    path('<str:expense_id>/delete/', delete_expense, name='delete_expense'),
]

# API versioning - these URLs will be prefixed with /api/v1/expenses/
app_name = 'expense_management'