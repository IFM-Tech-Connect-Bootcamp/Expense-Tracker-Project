"""Django implementation of ExpenseRepository.

This module provides a concrete implementation of the ExpenseRepository
interface using Django ORM for persistence.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q

from ...domain.entities.expense import Expense
from ...domain.errors import ExpenseNotFoundError, ExpenseAlreadyExistsError
from ...domain.repositories.expense_repository import ExpenseRepository
from ...domain.value_objects.expense_id import ExpenseId
from ...domain.value_objects.category_id import CategoryId
from ...domain.value_objects.user_id import UserId
from ...domain.value_objects.amount_tzs import AmountTZS
from ..orm.mappers import (
    expense_model_to_entity,
    expense_entity_to_model_data,
    create_expense_model_from_entity,
    update_expense_model_from_entity,
    validate_expense_model_data,
)
from ..orm.models import ExpenseModel

logger = logging.getLogger(__name__)


class DjangoExpenseRepository(ExpenseRepository):
    """Django ORM implementation of ExpenseRepository.
    
    Provides persistence operations for Expense entities using Django ORM.
    Handles mapping between domain entities and database models.
    Translates database errors to domain errors.
    """

    def find_by_id(self, expense_id: ExpenseId) -> Optional[Expense]:
        """Find expense by ID.
        
        Args:
            expense_id: Unique expense identifier.
            
        Returns:
            Expense entity if found, None otherwise.
            
        Raises:
            ValueError: If database data is invalid for domain entity.
        """
        logger.debug(f"Finding expense by ID: {expense_id.value}")
        
        try:
            model = ExpenseModel.objects.get(id=expense_id.value)
            expense = expense_model_to_entity(model)
            logger.debug(f"Found expense: {expense.id.value}")
            return expense
        except ObjectDoesNotExist:
            logger.debug(f"Expense not found: {expense_id.value}")
            return None
        except Exception as e:
            logger.error(f"Error finding expense by ID {expense_id.value}: {e}")
            raise ValueError(f"Failed to find expense: {e}") from e

    def find_by_user_id(self, user_id: UserId, limit: int = 100, offset: int = 0) -> List[Expense]:
        """Find expenses by user ID with pagination.
        
        Args:
            user_id: User identifier.
            limit: Maximum number of expenses to return.
            offset: Number of expenses to skip.
            
        Returns:
            List of expense entities belonging to the user.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding expenses for user: {user_id.value} (limit={limit}, offset={offset})")
        
        try:
            models = ExpenseModel.objects.filter(
                user_id=user_id.value
            ).order_by('-expense_date', '-created_at')[offset:offset + limit]
            
            expenses = []
            for model in models:
                expense = expense_model_to_entity(model)
                expenses.append(expense)
            
            logger.debug(f"Found {len(expenses)} expenses for user {user_id.value}")
            return expenses
            
        except Exception as e:
            logger.error(f"Error finding expenses for user {user_id.value}: {e}")
            raise ValueError(f"Failed to find expenses: {e}") from e

    def find_by_user_and_category(self, user_id: UserId, category_id: CategoryId, 
                                 limit: int = 100, offset: int = 0) -> List[Expense]:
        """Find expenses by user and category with pagination.
        
        Args:
            user_id: User identifier.
            category_id: Category identifier.
            limit: Maximum number of expenses to return.
            offset: Number of expenses to skip.
            
        Returns:
            List of expense entities for the user and category.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding expenses for user {user_id.value} and category {category_id.value}")
        
        try:
            models = ExpenseModel.objects.filter(
                user_id=user_id.value,
                category_id=category_id.value
            ).order_by('-expense_date', '-created_at')[offset:offset + limit]
            
            expenses = []
            for model in models:
                expense = expense_model_to_entity(model)
                expenses.append(expense)
            
            logger.debug(f"Found {len(expenses)} expenses for user {user_id.value} and category {category_id.value}")
            return expenses
            
        except Exception as e:
            logger.error(f"Error finding expenses for user {user_id.value} and category {category_id.value}: {e}")
            raise ValueError(f"Failed to find expenses: {e}") from e

    def find_by_date_range(self, user_id: UserId, start_date: date, end_date: date,
                          limit: int = 100, offset: int = 0) -> List[Expense]:
        """Find expenses by user within date range.
        
        Args:
            user_id: User identifier.
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            limit: Maximum number of expenses to return.
            offset: Number of expenses to skip.
            
        Returns:
            List of expense entities within the date range.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding expenses for user {user_id.value} between {start_date} and {end_date}")
        
        try:
            models = ExpenseModel.objects.filter(
                user_id=user_id.value,
                expense_date__gte=start_date,
                expense_date__lte=end_date
            ).order_by('-expense_date', '-created_at')[offset:offset + limit]
            
            expenses = []
            for model in models:
                expense = expense_model_to_entity(model)
                expenses.append(expense)
            
            logger.debug(f"Found {len(expenses)} expenses for user {user_id.value} in date range")
            return expenses
            
        except Exception as e:
            logger.error(f"Error finding expenses by date range for user {user_id.value}: {e}")
            raise ValueError(f"Failed to find expenses: {e}") from e

    def calculate_total_amount(self, user_id: UserId, start_date: Optional[date] = None,
                              end_date: Optional[date] = None, 
                              category_id: Optional[CategoryId] = None) -> AmountTZS:
        """Calculate total amount of expenses for user with optional filters.
        
        Args:
            user_id: User identifier.
            start_date: Optional start date filter.
            end_date: Optional end date filter.
            category_id: Optional category filter.
            
        Returns:
            Total amount as AmountTZS value object.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Calculating total amount for user {user_id.value}")
        
        try:
            query = Q(user_id=user_id.value)
            
            if start_date:
                query &= Q(expense_date__gte=start_date)
            if end_date:
                query &= Q(expense_date__lte=end_date)
            if category_id:
                query &= Q(category_id=category_id.value)
            
            total = ExpenseModel.objects.filter(query).aggregate(
                total=Sum('amount_tzs')
            )['total']
            
            # Handle case when no expenses found
            if total is None:
                total = Decimal('0.00')
            
            amount = AmountTZS.from_decimal(total)
            logger.debug(f"Total amount calculated: {amount.to_formatted_string()}")
            return amount
            
        except Exception as e:
            logger.error(f"Error calculating total amount for user {user_id.value}: {e}")
            raise ValueError(f"Failed to calculate total amount: {e}") from e

    def count_by_user(self, user_id: UserId) -> int:
        """Count expenses for a user.
        
        Args:
            user_id: User identifier.
            
        Returns:
            Number of expenses for the user.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Counting expenses for user: {user_id.value}")
        
        try:
            count = ExpenseModel.objects.filter(user_id=user_id.value).count()
            logger.debug(f"Found {count} expenses for user {user_id.value}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting expenses for user {user_id.value}: {e}")
            raise ValueError(f"Failed to count expenses: {e}") from e

    def exists_by_id(self, expense_id: ExpenseId) -> bool:
        """Check if expense exists by ID.
        
        Args:
            expense_id: Expense identifier.
            
        Returns:
            True if expense exists, False otherwise.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Checking if expense exists: {expense_id.value}")
        
        try:
            exists = ExpenseModel.objects.filter(id=expense_id.value).exists()
            logger.debug(f"Expense exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking expense existence {expense_id.value}: {e}")
            raise ValueError(f"Failed to check expense existence: {e}") from e

    def save(self, expense: Expense) -> Expense:
        """Save new expense to database.
        
        Args:
            expense: Expense entity to save.
            
        Returns:
            Saved expense entity with any generated fields.
            
        Raises:
            ExpenseAlreadyExistsError: If expense with same ID already exists.
            ValueError: If expense data is invalid.
        """
        logger.debug(f"Saving new expense: {expense.id.value}")
        
        try:
            # Check if expense already exists
            if self.exists_by_id(expense.id):
                raise ExpenseAlreadyExistsError(f"Expense with ID {expense.id.value} already exists")
            
            # Create new model
            model_data = expense_entity_to_model_data(expense)
            validate_expense_model_data(model_data)
            
            model = ExpenseModel.objects.create(**model_data)
            logger.info(f"Expense saved with ID: {model.id}")
            
            # Convert back to entity and return
            saved_expense = expense_model_to_entity(model)
            return saved_expense
                
        except IntegrityError as e:
            logger.error(f"Database integrity error saving expense: {e}")
            if "id" in str(e).lower():
                raise ExpenseAlreadyExistsError(f"Expense with ID {expense.id.value} already exists")
            raise ValueError(f"Invalid expense data: {e}")
        except Exception as e:
            logger.error(f"Error saving expense {expense.id.value}: {e}")
            raise

    def update(self, expense: Expense) -> Expense:
        """Update existing expense entity in database.
        
        Args:
            expense: Expense entity to update.
            
        Returns:
            Updated expense entity.
            
        Raises:
            ExpenseNotFoundError: If expense doesn't exist.
            ValueError: If update operation fails.
        """
        logger.debug(f"Updating expense: {expense.id.value}")
        
        try:
            # Get existing model
            try:
                existing_model = ExpenseModel.objects.get(id=expense.id.value)
            except ObjectDoesNotExist:
                logger.warning(f"Expense not found for update: {expense.id.value}")
                raise ExpenseNotFoundError(str(expense.id.value))
            
            # Update model with new data
            try:
                updated_model = update_expense_model_from_entity(existing_model, expense)
                updated_model.save()
            except IntegrityError as e:
                logger.error(f"Database integrity error updating expense: {e}")
                raise ValueError(f"Database integrity error: {e}") from e
            
            # Return updated entity
            updated_expense = expense_model_to_entity(updated_model)
                
            logger.info(f"Successfully updated expense: {expense.id.value}")
            return updated_expense
            
        except (ExpenseNotFoundError,):
            raise
        except Exception as e:
            logger.error(f"Error updating expense {expense.id.value}: {e}")
            raise ValueError(f"Failed to update expense: {e}") from e

    def delete(self, expense_id: ExpenseId) -> None:
        """Delete expense from database.
        
        Args:
            expense_id: ID of expense to delete.
            
        Raises:
            ExpenseNotFoundError: If expense doesn't exist.
            ValueError: If delete operation fails.
        """
        logger.debug(f"Deleting expense: {expense_id.value}")
        
        try:
            try:
                model = ExpenseModel.objects.get(id=expense_id.value)
                model.delete()
            except ObjectDoesNotExist:
                logger.warning(f"Expense not found for deletion: {expense_id.value}")
                raise ExpenseNotFoundError(str(expense_id.value))
            
            logger.info(f"Successfully deleted expense: {expense_id.value}")
            
        except ExpenseNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id.value}: {e}")
            raise ValueError(f"Failed to delete expense: {e}") from e

    def delete_by_category(self, category_id: CategoryId) -> int:
        """Delete all expenses for a category.
        
        Args:
            category_id: Category identifier.
            
        Returns:
            Number of expenses deleted.
            
        Raises:
            ValueError: If delete operation fails.
        """
        logger.debug(f"Deleting expenses for category: {category_id.value}")
        
        try:
            deleted_count, _ = ExpenseModel.objects.filter(
                category_id=category_id.value
            ).delete()
            
            logger.info(f"Deleted {deleted_count} expenses for category {category_id.value}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting expenses for category {category_id.value}: {e}")
            raise ValueError(f"Failed to delete expenses: {e}") from e

    def find_recent_expenses(self, user_id: UserId, limit: int = 10) -> List[Expense]:
        """Find most recent expenses for a user.
        
        Args:
            user_id: User identifier.
            limit: Maximum number of expenses to return.
            
        Returns:
            List of recent expense entities ordered by date/time descending.
            
        Raises:
            ValueError: If database query fails.
        """
        logger.debug(f"Finding recent expenses for user: {user_id.value} (limit={limit})")
        
        try:
            models = ExpenseModel.objects.filter(
                user_id=user_id.value
            ).order_by('-expense_date', '-created_at')[:limit]
            
            expenses = []
            for model in models:
                expense = expense_model_to_entity(model)
                expenses.append(expense)
            
            logger.debug(f"Found {len(expenses)} recent expenses for user {user_id.value}")
            return expenses
            
        except Exception as e:
            logger.error(f"Error finding recent expenses for user {user_id.value}: {e}")
            raise ValueError(f"Failed to find recent expenses: {e}") from e