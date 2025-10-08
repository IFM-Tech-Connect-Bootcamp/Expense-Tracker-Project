"""
Serializers for Expense Management API endpoints.

This module contains Django REST Framework serializers that handle
request/response serialization for the expense management presentation layer.
All serializers follow clean architecture principles by depending only
on DTOs and not directly on domain entities.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from typing import Dict, Any, Optional
from decimal import Decimal, InvalidOperation
from datetime import date, datetime


class CreateExpenseSerializer(serializers.Serializer):
    """Serializer for expense creation requests."""
    
    category_id = serializers.UUIDField(
        help_text="ID of the category for this expense"
    )
    amount_tzs = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text="Expense amount in Tanzanian Shillings (minimum: 0.01 TZS)"
    )
    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Optional description of the expense (max 500 characters)"
    )
    expense_date = serializers.DateField(
        help_text="Date when the expense occurred (YYYY-MM-DD)"
    )

    def validate_amount_tzs(self, value: Decimal) -> float:
        """Validate TZS amount and convert to float."""
        if value <= 0:
            raise ValidationError("Amount must be greater than zero")
        if value > Decimal('1000000.00'):  # 1M TZS limit
            raise ValidationError("Amount cannot exceed 1,000,000.00 TZS")
        return float(value)

    def validate_description(self, value: str) -> Optional[str]:
        """Validate and normalize description."""
        if not value or not value.strip():
            return None
        return value.strip()

    def validate_expense_date(self, value: date) -> date:
        """Validate expense date."""
        if value > date.today():
            raise ValidationError("Expense date cannot be in the future")
        return value


class UpdateExpenseSerializer(serializers.Serializer):
    """Serializer for expense update requests."""
    
    category_id = serializers.UUIDField(
        required=False,
        help_text="New category ID for the expense"
    )
    amount_tzs = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=False,
        help_text="New expense amount in Tanzanian Shillings"
    )
    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="New description for the expense"
    )
    expense_date = serializers.DateField(
        required=False,
        help_text="New expense date (YYYY-MM-DD)"
    )

    def validate_amount_tzs(self, value: Decimal) -> float:
        """Validate TZS amount and convert to float."""
        if value <= 0:
            raise ValidationError("Amount must be greater than zero")
        if value > Decimal('1000000.00'):
            raise ValidationError("Amount cannot exceed 1,000,000.00 TZS")
        return float(value)

    def validate_description(self, value: str) -> str:
        """Validate and normalize description."""
        return value.strip() if value else value

    def validate_expense_date(self, value: date) -> date:
        """Validate expense date."""
        if value > date.today():
            raise ValidationError("Expense date cannot be in the future")
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that at least one field is provided for update."""
        if not attrs:
            raise ValidationError("At least one field must be provided for update")
        return attrs


class CreateCategorySerializer(serializers.Serializer):
    """Serializer for category creation requests."""
    
    name = serializers.CharField(
        max_length=100,
        min_length=2,
        help_text="Category name (2-100 characters)"
    )

    def validate_name(self, value: str) -> str:
        """Validate and normalize category name."""
        name = value.strip()
        if not name:
            raise ValidationError("Category name cannot be empty")
        if len(name) < 2:
            raise ValidationError("Category name must be at least 2 characters")
        return name.title()


class UpdateCategorySerializer(serializers.Serializer):
    """Serializer for category update requests."""
    
    name = serializers.CharField(
        max_length=100,
        min_length=2,
        help_text="New category name (2-100 characters)"
    )

    def validate_name(self, value: str) -> str:
        """Validate and normalize category name."""
        name = value.strip()
        if not name:
            raise ValidationError("Category name cannot be empty")
        if len(name) < 2:
            raise ValidationError("Category name must be at least 2 characters")
        return name.title()


class ExpenseSummaryQuerySerializer(serializers.Serializer):
    """Serializer for expense summary query parameters."""
    
    start_date = serializers.DateField(
        required=False,
        help_text="Start date for expense summary (YYYY-MM-DD)"
    )
    end_date = serializers.DateField(
        required=False,
        help_text="End date for expense summary (YYYY-MM-DD)"
    )
    category_id = serializers.UUIDField(
        required=False,
        help_text="Filter by specific category ID"
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate date range."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before or equal to end date")
            if end_date > date.today():
                raise ValidationError("End date cannot be in the future")
        elif end_date and not start_date:
            if end_date > date.today():
                raise ValidationError("End date cannot be in the future")
        
        return attrs


# Response Serializers

class ExpenseResponseSerializer(serializers.Serializer):
    """Serializer for expense response data."""
    
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(read_only=True)
    category_id = serializers.UUIDField(read_only=True)
    amount_tzs = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    amount_formatted = serializers.CharField(
        read_only=True,
        help_text="Formatted TZS amount string"
    )
    description = serializers.CharField(
        read_only=True,
        allow_null=True
    )
    expense_date = serializers.DateField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CategoryResponseSerializer(serializers.Serializer):
    """Serializer for category response data."""
    
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CategorySummaryResponseSerializer(serializers.Serializer):
    """Serializer for category summary data."""
    
    category_id = serializers.UUIDField(read_only=True)
    category_name = serializers.CharField(read_only=True)
    total_amount_tzs = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_amount_formatted = serializers.CharField(
        read_only=True,
        help_text="Formatted TZS total amount"
    )
    expense_count = serializers.IntegerField(read_only=True)
    average_amount_tzs = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    average_amount_formatted = serializers.CharField(
        read_only=True,
        help_text="Formatted TZS average amount"
    )


class ExpenseSummaryResponseSerializer(serializers.Serializer):
    """Serializer for expense summary response data."""
    
    user_id = serializers.UUIDField(read_only=True)
    total_amount_tzs = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_amount_formatted = serializers.CharField(
        read_only=True,
        help_text="Formatted TZS total amount"
    )
    expense_count = serializers.IntegerField(read_only=True)
    average_amount_tzs = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    average_amount_formatted = serializers.CharField(
        read_only=True,
        help_text="Formatted TZS average amount"
    )
    start_date = serializers.DateField(
        read_only=True,
        allow_null=True
    )
    end_date = serializers.DateField(
        read_only=True,
        allow_null=True
    )
    category_summaries = CategorySummaryResponseSerializer(
        many=True,
        read_only=True
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error response format."""
    
    error = serializers.CharField(help_text="Error message")
    code = serializers.CharField(
        required=False,
        help_text="Error code for client handling"
    )
    details = serializers.DictField(
        required=False,
        help_text="Additional error details"
    )


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for success response format."""
    
    message = serializers.CharField(help_text="Success message")
    data = serializers.DictField(
        required=False,
        help_text="Optional response data"
    )