"""
Expense Management Domain Layer

This package contains the domain layer for the expense management bounded context.
The domain layer represents the core business logic and rules of expense management.

Components:
- value_objects: Immutable objects representing domain concepts
- entities: Objects with identity that encapsulate business behavior  
- repositories: Interfaces for data persistence contracts
- services: Domain services for business logic that spans entities
- events: Domain events representing significant business occurrences
- enums: Enumerations for fixed sets of domain values
- errors: Domain-specific error conditions

The domain layer is technology-agnostic and contains pure business logic.
"""

from .value_objects import (
    ExpenseId, CategoryId, UserId, AmountTZS, 
    ExpenseDescription, CategoryName
)
from .entities import Expense, Category
from .repositories import (
    ExpenseRepository, CategoryRepository,
    RepositoryError, TransactionManager
)
from .services import (
    ExpenseSummaryService, CategoryValidationService, 
    DefaultCategoryService
)
from .events import (
    DomainEvent, ExpenseCreated, ExpenseUpdated, ExpenseDeleted,
    CategoryCreated, CategoryUpdated, CategoryDeleted
)
from .enums import ExpenseStatus
from .errors import (
    ExpenseManagementDomainError, ExpenseError, CategoryError,
    ExpenseNotFoundError, ExpenseAccessDeniedError, InvalidExpenseDataError,
    CategoryNotFoundError, CategoryAccessDeniedError, DuplicateCategoryNameError,
    CategoryInUseError, InvalidCategoryDataError, UserNotFoundError,
    BusinessRuleViolationError, ValidationError
)

__all__ = [
    # Value Objects
    'ExpenseId', 'CategoryId', 'UserId', 'AmountTZS', 
    'ExpenseDescription', 'CategoryName',
    
    # Entities
    'Expense', 'Category',
    
    # Repositories
    'ExpenseRepository', 'CategoryRepository',
    'RepositoryError', 'TransactionManager',
    
    # Services
    'ExpenseSummaryService', 'CategoryValidationService', 
    'DefaultCategoryService',
    
    # Events
    'DomainEvent', 'ExpenseCreated', 'ExpenseUpdated', 'ExpenseDeleted',
    'CategoryCreated', 'CategoryUpdated', 'CategoryDeleted',
    
    # Enums
    'ExpenseStatus',
    
    # Errors
    'ExpenseManagementDomainError', 'ExpenseError', 'CategoryError',
    'ExpenseNotFoundError', 'ExpenseAccessDeniedError', 'InvalidExpenseDataError',
    'CategoryNotFoundError', 'CategoryAccessDeniedError', 'DuplicateCategoryNameError',
    'CategoryInUseError', 'InvalidCategoryDataError', 'UserNotFoundError',
    'BusinessRuleViolationError', 'ValidationError'
]
