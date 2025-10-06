"""Application layer for Expense Management bounded context.

This package contains the application layer implementation that orchestrates
business use cases and coordinates between the domain layer and infrastructure concerns.

The application layer provides:
- Command objects for use case inputs
- Command handlers for business workflow orchestration  
- Data Transfer Objects (DTOs) for external communication
- Event bus for domain event publishing
- Service orchestration for high-level coordination
- Error translation from domain to application concerns

Architecture:
- Synchronous operations for team maintainability
- Command-handler pattern for clear use case separation
- Event-driven architecture for decoupled side effects
- Protocol-based dependency injection for testability
- Comprehensive error handling and logging
"""

from .commands import (
    CreateExpenseCommand,
    UpdateExpenseCommand,
    DeleteExpenseCommand,
    CreateCategoryCommand,
    UpdateCategoryCommand,
    DeleteCategoryCommand,
    GetExpenseSummaryCommand,
)

from .handlers import (
    CreateExpenseHandler,
    UpdateExpenseHandler,
    DeleteExpenseHandler,
    CreateCategoryHandler,
    UpdateCategoryHandler,
    DeleteCategoryHandler,
    GetExpenseSummaryHandler,
)

from .dto import (
    ExpenseDTO,
    CategoryDTO,
    ExpenseSummaryDTO,
    CategorySummaryDTO,
)

from .service import ExpenseManagementService
from .event_bus import event_bus
from .errors import (
    ApplicationError,
    ExpenseCreationFailedError,
    ExpenseUpdateFailedError,
    ExpenseDeleteFailedError,
    ExpenseNotFoundError,
    ExpenseAccessDeniedError,
    CategoryCreationFailedError,
    CategoryUpdateFailedError,
    CategoryDeleteFailedError,
    CategoryNotFoundError,
    CategoryAccessDeniedError,
    DuplicateCategoryNameError,
    CategoryInUseError,
    ExpenseSummaryFailedError,
    UserNotFoundError,
    ValidationError,
    BusinessRuleViolationError,
    translate_domain_error,
)

__all__ = [
    # Commands
    "CreateExpenseCommand",
    "UpdateExpenseCommand",
    "DeleteExpenseCommand",
    "CreateCategoryCommand",
    "UpdateCategoryCommand",
    "DeleteCategoryCommand",
    "GetExpenseSummaryCommand",
    
    # Handlers
    "CreateExpenseHandler",
    "UpdateExpenseHandler",
    "DeleteExpenseHandler",
    "CreateCategoryHandler",
    "UpdateCategoryHandler",
    "DeleteCategoryHandler",
    "GetExpenseSummaryHandler",
    
    # DTOs
    "ExpenseDTO",
    "CategoryDTO",
    "ExpenseSummaryDTO",
    "CategorySummaryDTO",
    
    # Service
    "ExpenseManagementService",
    
    # Event Bus
    "event_bus",
    
    # Errors
    "ApplicationError",
    "ExpenseCreationFailedError",
    "ExpenseUpdateFailedError",
    "ExpenseDeleteFailedError",
    "ExpenseNotFoundError",
    "ExpenseAccessDeniedError",
    "CategoryCreationFailedError",
    "CategoryUpdateFailedError",
    "CategoryDeleteFailedError",
    "CategoryNotFoundError",
    "CategoryAccessDeniedError",
    "DuplicateCategoryNameError",
    "CategoryInUseError",
    "ExpenseSummaryFailedError",
    "UserNotFoundError",
    "ValidationError",
    "BusinessRuleViolationError",
    "translate_domain_error",
]