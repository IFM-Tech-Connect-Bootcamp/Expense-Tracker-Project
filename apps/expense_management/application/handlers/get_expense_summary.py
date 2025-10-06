"""Get expense summary handler.

This module contains the handler for expense summary query use cases.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Dict

from ...domain.entities.expense import Expense
from ...domain.entities.category import Category
from ...domain.errors import ExpenseManagementDomainError
from ...domain.repositories.expense_repository import ExpenseRepository
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.value_objects.user_id import UserId
from ...domain.value_objects.category_id import CategoryId
from ...domain.services.expense_summary_service import ExpenseSummaryService
from ..commands.get_expense_summary import GetExpenseSummaryCommand
from ..errors import translate_domain_error, ExpenseSummaryFailedError, ApplicationError
from ..dto import ExpenseSummaryDTO, CategorySummaryDTO

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetExpenseSummaryResult:
    """Result of expense summary query operation."""
    summary_dto: ExpenseSummaryDTO


class GetExpenseSummaryHandler:
    """Handler for expense summary query operations.
    
    This handler orchestrates the expense summary use case by:
    1. Validating the expense summary request
    2. Fetching user's expenses with optional filters
    3. Fetching user's categories for summary enrichment
    4. Calculating expense totals and aggregations
    5. Building category-wise summaries
    6. Returning a comprehensive expense summary DTO
    """
    
    def __init__(
        self,
        expense_repository: ExpenseRepository,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize the get expense summary handler.
        
        Args:
            expense_repository: Repository for expense query operations.
            category_repository: Repository for category query operations.
        """
        self._expense_repository = expense_repository
        self._category_repository = category_repository
    
    def handle(self, command: GetExpenseSummaryCommand) -> GetExpenseSummaryResult:
        """Execute the expense summary query use case.
        
        Args:
            command: The query command containing filter criteria.
            
        Returns:
            GetExpenseSummaryResult containing comprehensive expense summary.
            
        Raises:
            ApplicationError: If expense summary generation fails for any reason.
        """
        logger.info(f"Executing expense summary query for user: {command.user_id}")
        
        try:
            # Step 1: Validate the expense summary request
            logger.debug(f"Validating expense summary request for user: {command.user_id}")
            
            # Create domain value objects
            user_id = UserId.from_string(command.user_id)
            category_filter = CategoryId.from_string(command.category_id) if command.category_id else None
            
            # Step 2: Fetch user's expenses with filters
            logger.debug(f"Fetching expenses for user {command.user_id} with filters")
            
            if command.has_date_filter() or command.has_category_filter():
                # Apply filters
                expenses = self._expense_repository.find_by_user_id_with_filters(
                    user_id=user_id,
                    start_date=command.start_date,
                    end_date=command.end_date,
                    category_id=category_filter
                )
            else:
                # No filters - get all user expenses
                expenses = self._expense_repository.find_by_user_id(user_id)
            
            # Step 3: Fetch user's categories for summary enrichment
            logger.debug(f"Fetching categories for user {command.user_id}")
            categories = self._category_repository.find_by_user_id(user_id)
            category_map = {cat.id: cat for cat in categories}
            
            # Step 4: Calculate overall totals using domain service
            logger.debug(f"Calculating expense totals for {len(expenses)} expenses")
            total_amount = ExpenseSummaryService.calculate_total_amount(expenses)
            total_count = len(expenses)
            average_amount = ExpenseSummaryService.calculate_average_expense_amount(expenses)
            
            # Step 5: Build category-wise summaries
            logger.debug(f"Building category summaries")
            category_totals = ExpenseSummaryService.calculate_total_by_category(expenses)
            category_counts = ExpenseSummaryService.count_expenses_by_category(expenses)
            
            category_summaries: List[CategorySummaryDTO] = []
            for category_id_val, total_amount_val in category_totals.items():
                category = category_map.get(category_id_val)
                expense_count = category_counts.get(category_id_val, 0)
                
                if category and expense_count > 0:
                    average_for_category = total_amount_val.value / expense_count
                    
                    category_summary = CategorySummaryDTO(
                        category_id=str(category_id_val.value),
                        category_name=category.name.value,
                        total_amount_tzs=total_amount_val.value,
                        expense_count=expense_count,
                        average_amount_tzs=average_for_category
                    )
                    category_summaries.append(category_summary)
            
            # Sort by total amount descending
            category_summaries.sort(key=lambda cat: cat.total_amount_tzs, reverse=True)
            
            # Step 6: Create expense summary DTO
            logger.debug(f"Creating expense summary DTO for user {command.user_id}")
            summary_dto = ExpenseSummaryDTO(
                user_id=command.user_id,
                total_amount_tzs=total_amount.value,
                total_expense_count=total_count,
                average_expense_amount_tzs=average_amount.value,
                start_date=command.start_date,
                end_date=command.end_date,
                category_summaries=category_summaries
            )
            
            logger.info(f"Expense summary completed successfully for user {command.user_id}: {total_count} expenses, TZS {total_amount.value:,.2f} total")
            
            return GetExpenseSummaryResult(
                summary_dto=summary_dto
            )
            
        except ExpenseManagementDomainError as e:
            logger.error(f"Domain error during expense summary for user {command.user_id}: {str(e)}")
            raise translate_domain_error(e) from e
        except Exception as e:
            logger.error(f"Unexpected error during expense summary for user {command.user_id}: {str(e)}")
            raise ExpenseSummaryFailedError(f"Failed to generate expense summary: {str(e)}") from e