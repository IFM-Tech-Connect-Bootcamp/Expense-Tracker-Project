"""
Presentation layer for Expense Management bounded context.

This package contains the presentation layer implementation that handles HTTP requests
and responses for expense and category management operations. It provides RESTful API
endpoints following Django REST Framework patterns while maintaining Clean Architecture
principles.

The presentation layer includes:
- API view functions for expense and category management
- Request/response serializers for data validation and formatting
- Authentication utilities integrating with User Management context
- URL routing configuration for RESTful endpoints
- OpenAPI documentation for comprehensive API specification

Architecture:
- RESTful API design with standard HTTP methods and status codes
- Synchronous operations for simplified debugging and maintenance
- JWT-based authentication integration with User Management context
- Comprehensive error handling with structured error responses
- TZS currency-specific formatting and validation
- Clean separation between HTTP concerns and business logic

API Endpoints:
- POST /expenses/ - Create new expense
- PUT /expenses/{id}/ - Update existing expense  
- DELETE /expenses/{id}/delete/ - Delete expense
- GET /expenses/summary/ - Get expense analytics summary
- POST /categories/ - Create new category
- PUT /categories/{id}/ - Update existing category
- DELETE /categories/{id}/delete/ - Delete category
- GET /health/ - Service health check
"""

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

from .serializers import (
    CreateExpenseSerializer,
    UpdateExpenseSerializer,
    CreateCategorySerializer,
    UpdateCategorySerializer,
    ExpenseSummaryQuerySerializer,
    ExpenseResponseSerializer,
    CategoryResponseSerializer,
    ExpenseSummaryResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)

from .authentication import (
    get_current_user_from_request,
    verify_expense_ownership,
    verify_category_ownership,
)

__all__ = [
    # Views
    "create_expense",
    "update_expense",
    "delete_expense",
    "get_expense_summary",
    "create_category",
    "update_category",
    "delete_category",
    "expense_health_check",
    
    # Serializers
    "CreateExpenseSerializer",
    "UpdateExpenseSerializer",
    "CreateCategorySerializer",
    "UpdateCategorySerializer",
    "ExpenseSummaryQuerySerializer",
    "ExpenseResponseSerializer",
    "CategoryResponseSerializer",
    "ExpenseSummaryResponseSerializer",
    "ErrorResponseSerializer",
    "SuccessResponseSerializer",
    
    # Authentication
    "get_current_user_from_request",
    "verify_expense_ownership",
    "verify_category_ownership",
]