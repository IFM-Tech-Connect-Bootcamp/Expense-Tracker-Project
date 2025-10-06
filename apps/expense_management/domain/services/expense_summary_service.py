"""
Expense Management Domain - Expense Summary Service

This module contains the ExpenseSummaryService for calculating expense summaries and totals.
Domain services contain pure business logic without infrastructure dependencies.
"""

from decimal import Decimal
from typing import List, Dict

from ..entities import Expense
from ..value_objects import AmountTZS


class ExpenseSummaryService:
    """
    Domain service for calculating expense summaries and totals.
    
    Provides pure business logic for aggregating and analyzing expense data.
    This service operates on collections of expenses passed to it,
    following the same pattern as User Management domain services.
    """

    @staticmethod
    def calculate_total_amount(expenses: List[Expense]) -> AmountTZS:
        """Calculate the total amount from a list of expenses."""
        total = Decimal('0.00')
        
        for expense in expenses:
            total += expense.amount_tzs.value
        
        return AmountTZS(value=total)

    @staticmethod
    def calculate_total_by_category(expenses: List[Expense]) -> Dict[str, AmountTZS]:
        """Calculate total amounts by category from a list of expenses."""
        category_totals = {}
        
        for expense in expenses:
            category_id_str = str(expense.category_id)
            if category_id_str not in category_totals:
                category_totals[category_id_str] = Decimal('0.00')
            category_totals[category_id_str] += expense.amount_tzs.value
        
        return {
            category_id: AmountTZS(value=total) 
            for category_id, total in category_totals.items()
        }

    @staticmethod
    def get_expense_count_by_category(expenses: List[Expense]) -> Dict[str, int]:
        """Get count of expenses by category from a list of expenses."""
        category_counts = {}
        
        for expense in expenses:
            category_id_str = str(expense.category_id)
            if category_id_str not in category_counts:
                category_counts[category_id_str] = 0
            category_counts[category_id_str] += 1
        
        return category_counts

    @staticmethod
    def calculate_average_expense_amount(expenses: List[Expense]) -> AmountTZS:
        """Calculate the average expense amount from a list of expenses."""
        if not expenses:
            return AmountTZS(value=Decimal('0.00'))
        
        total = ExpenseSummaryService.calculate_total_amount(expenses)
        average = total.value / len(expenses)
        
        return AmountTZS(value=average)